import argparse
import sys
from rich.console import Console
from rich.markdown import Markdown
from src.rag_engine import get_answer
from src.session import load_history, save_history, generate_session_id

console = Console()

def process_query(query, history, verbose=True):
    with console.status("[bold green]Denke nach...", spinner="dots"):
        # Wir entpacken jetzt 4 Rückgabewerte
        answer, sources, prompt, context = get_answer(query, history)
    
    if verbose:
        console.print("\n[bold yellow]--- Gefundener Kontext (Vector DB) ---[/bold yellow]")
        # Zeige nur die ersten 500 Zeichen pro Dokument im Kontext, damit es nicht den Screen flutet
        # oder den vollen Kontext, wenn gewünscht. Hier zeigen wir es kompakt.
        console.print(context)
        
        console.print("\n[bold yellow]--- Generierter Prompt an Gemini ---[/bold yellow]")
        console.print(prompt)
        console.print("\n" + "-"*50 + "\n")

    # Antwort ausgeben
    console.print("[bold blue]--- Antwort ---[/bold blue]")
    console.print(Markdown(answer))
    
    if verbose and sources:
        console.print("\n[dim]Quellen-Liste:[/dim]")
        for s in sources:
            console.print(f"[dim]- {s}[/dim]")
    console.print("")
    
    return answer

def main():
    parser = argparse.ArgumentParser(description="Juristischer AI Agent (RAG)")
    parser.add_argument("query", type=str, nargs="?", help="Deine Rechtsfrage (optional im interaktiven Modus)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interaktiver Chat-Modus")
    parser.add_argument("--session", type=str, help="Session-ID zum Laden/Speichern des Verlaufs")
    parser.add_argument("-q", "--quiet", action="store_true", help="Weniger Ausgaben (kein Prompt/Kontext)")
    
    args = parser.parse_args()
    
    # Session Management
    session_id = args.session
    history = []
    
    if session_id:
        history = load_history(session_id)
        console.print(f"[bold blue]Session geladen: {session_id} ({len(history)} Nachrichten)[/bold blue]")
    elif args.interactive:
        session_id = generate_session_id()
        console.print(f"[bold blue]Neue Session gestartet: {session_id}[/bold blue]")

    # Modus 1: Einzelne Abfrage
    if args.query:
        answer = process_query(args.query, history, not args.quiet)
        
        if session_id:
            history.append({"role": "user", "content": args.query})
            history.append({"role": "assistant", "content": answer})
            save_history(session_id, history)
            
        if not args.interactive:
            return

    # Modus 2: Interaktiver Loop
    if args.interactive:
        console.print("[bold green]Interaktiver Modus gestartet. 'exit' oder 'quit' zum Beenden.[/bold green]\n")
        
        while True:
            try:
                user_input = console.input("[bold yellow]Du:[/bold yellow] ")
                
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                if not user_input.strip():
                    continue
                
                answer = process_query(user_input, history, not args.quiet)
                
                # Update History
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": answer})
                
                if session_id:
                    save_history(session_id, history)
                    
            except KeyboardInterrupt:
                console.print("\nBeendet.")
                break

if __name__ == "__main__":
    main()