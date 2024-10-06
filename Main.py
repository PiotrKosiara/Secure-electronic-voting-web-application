import Database_interaction_functions

Database_interaction_functions.create_database()

Database_interaction_functions.add_candidate("Kandydat_A")
Database_interaction_functions.add_candidate("Kandydat_B")

Database_interaction_functions.register_voter("Jan", "password1")
Database_interaction_functions.register_voter("Anna", "password2")


# Database_interaction_functions.register_voter("Jan Kowalski")
# Database_interaction_functions.register_voter("Anna Nowak")

# Database_interaction_functions.cast_vote(1, 1)
# Database_interaction_functions.cast_vote(2, 2)

# Database_interaction_functions.show_results()