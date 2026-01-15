# salva_tutto_il_codice.py
import os
from pathlib import Path

def salva_contenuti_python(
    cartella_partenza=None,
    file_output="TUTTO_IL_CODICE_PROGETTO.txt",
    escludi_cartelle=["__pycache__", ".git", "dist", "build", "state", "logs", "exports", "screenshots"]
):
    """
    Salva tutto il codice .py del progetto (inclusi file alla root!)
    → Esclude cartelle inutili
    → Salta se stesso (opzionale)
    → Formattazione bellissima con separatori
    → Salva anche run.py, make_exe.py, ecc.
    """
    if cartella_partenza is None:
        cartella_partenza = Path.cwd()
    cartella_partenza = Path(cartella_partenza).resolve()
    output_path = cartella_partenza / file_output

    print(f"Avvio salvataggio di tutti i file .py da:\n  {cartella_partenza}\n")
    print(f"Output → {output_path}\n")
    print("═" * 90)

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(f"PROGETTO SERVICENOW AUTOMATION - CODICE COMPLETO\n")
        outfile.write(f"Generato il: {Path(__file__).name} – {os.popen('date').read().strip()}\n")
        # outfile.write(f"Cartella progetto: {cartella_partenza}\n")
        outfile.write("═" * 90 + "\n\n")

        file_count = 0
        for py_file in cartella_partenza.rglob("*.py"):
            # Escludi cartelle inutili
            if any(excluded in py_file.parts for excluded in escludi_cartelle):
                continue

            # Opzionale: escludi questo script stesso
            if py_file.resolve() == Path(__file__).resolve():
                continue

            file_count += 1
            print(f"{file_count:3d}. {py_file.relative_to(cartella_partenza)}")

            # Separatore bello
            outfile.write(f"\n{'='*30} FILE: {py_file.relative_to(cartella_partenza)} {'='*30}\n\n")

            try:
                contenuto = py_file.read_text(encoding="utf-8")
                outfile.write(contenuto)
            except Exception as e:
                outfile.write(f"!!! ERRORE LETTURA: {e}\n")

            outfile.write("\n" + "─" * 90 + "\n\n")

        outfile.write(f"\nFINE DOCUMENTO – {file_count} file .py salvati.\n")

    print("\n" + "═" * 90)
    print(f"COMPLETATO! {file_count} file Python salvati in:")
    print(f"   → {output_path}\n")
    print("Puoi copiarlo e incollarlo ovunque (Notion, Word, email, ecc.)\n")


# ESECUZIONE AUTOMATICA
if __name__ == "__main__":
    salva_contenuti_python()