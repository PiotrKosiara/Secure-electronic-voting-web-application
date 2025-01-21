import sqlite3
from cryptography.fernet import Fernet
import json
from Database_interaction_functions import decrypt_value_shamir

def count_votes():
    try:
        # Połączenie z bazą danych
        conn = sqlite3.connect('voting_system.db')
        c = conn.cursor()

        # Pobranie wszystkich zaszyfrowanych głosów
        c.execute('SELECT encrypted_vote FROM votes')
        encrypted_votes = c.fetchall()

        if not encrypted_votes:
            print("Brak głosów w bazie danych.")
            return

        # Odszyfrowanie i zliczanie głosów
        results = {}
        for encrypted_vote in encrypted_votes:
            try:
                decrypted_vote = decrypt_value_shamir(encrypted_vote[0])
                _, candidate = decrypted_vote.split(",candidate:")
                if candidate in results:
                    results[candidate] += 1
                else:
                    results[candidate] = 1
            except Exception as e:
                print(f"Błąd podczas odszyfrowywania głosu: {e}")

        # Wyświetlenie wyników
        print("Wyniki głosowania:")
        for candidate, count in results.items():
            print(f"{candidate}: {count} głosów")

    except sqlite3.Error as e:
        print(f"Błąd bazy danych: {e}")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    count_votes()