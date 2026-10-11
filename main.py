# TODO:
# Make terminal more friendly to bad inputs
# Clean up aesthetics of season stats plotting

from retro_bowl_fantasy_stats import *

def main():
    players = load_data()

    valid_terminal_actions = {
        "main": {"P", "E", "V"},
        "player hub": {"L", "D", "R", "S", "P", "X", "Z", "E"},
        "game lookup": {"R", "H", "E"}
    }

    terminal_initial_prompts = {
        "main": "Choose player [P], Display player list [V], or exit [E] \n",
        "player hub": "Log game [L]     Delete game [D]     Retrieve game [R]     Season stats [S] \nChoose different player[P]     Delete this player [X]     Retire this player [Z]     Exit [E] \n",
        "game lookup": "Retrieve another game [R]     Back to player hub [H]     Exit [E] \n"
    }

    terminal_reprompts = {
        "main": "Enter P to choose a player, V to display player list, or E to exit \n",
        "player hub": "Enter L to enter a game, D to delete a game, R to retrieve game data, S to retrieve season data, \nP to access a different player, X to delete this player, Z to retire this player, or E to exit. \n",
        "game lookup": "Enter R to retrieve another game, H to return to player hub, or E to exit. \n"
    }

    terminal_state = "main"
    terminal_action = None

    while terminal_action != "E":

        terminal_action = input(terminal_initial_prompts[terminal_state])

        # Handle all invalid terminal inputs before advancing
        while terminal_action not in valid_terminal_actions[terminal_state]:
            terminal_action = input(terminal_reprompts[terminal_state])

        if terminal_action == "V":
            display_known_players(players)
        
        if terminal_action == "P":
            # Player selection
            player_name = input("Player name? \n")

            if players.get(player_name) is None:
                confirm_new_player = input("Player name not in database. Create new player? [Y]/[N] \n")
                if confirm_new_player == "Y":
                    create_player(players, player_name)
                else:
                    continue

            player = players[player_name]

            terminal_state = "player hub"

        elif terminal_action == "X":
            # Player deletion
            confirm_delete_player = input(f"Are you sure you want to delete player {player_name}? \nYes [Y]     No [N] \n")

            while not (confirm_delete_player == "Y" or confirm_delete_player == "N"):
                confirm_delete_player = input("Enter Y to confirm player deletion or N to go back. \n")

            if confirm_delete_player == "Y":
                delete_player(players, player)
                print(f"Player {player_name} deleted. Returning to main menu. \n")
                terminal_state = "main"
            else:
                print("Player deletion canceled. \n")
                # terminal_state remains "player_hub"
        
        elif terminal_action == "Z":
            if is_retired(player):
                confirm_unretire_player = input("Player already retired. Unretire player? [Y]/[N]\n")
                while not (confirm_unretire_player == "Y" or confirm_unretire_player == "N"):
                    confirm_unretire_player = input("Enter Y to unretire player or N to go back. \n")

                if confirm_unretire_player == "Y":
                    unretire_player(player)
                    print(f"Player {player_name} unretired. \n")
                    # terminal_state remains "player_hub"

                else:
                    print("Player unretirement canceled. Returning to player hub. \n")
                    # terminal_state remains "player_hub"
            else:
                # Retire player
                confirm_retire_player = input(f"Are you sure you want to retire player {player_name}? \nYou will no longer be able to log new games for this player, but can still view stats.\nYes [Y]     No [N] \n")
                
                while not (confirm_retire_player == "Y" or confirm_retire_player == "N"):
                    confirm_retire_player = input("Enter Y to confirm player retirement or N to go back. \n")

                if confirm_retire_player == "Y":
                    retire_player(players, player)
                    print(f"Player {player_name} retired. \n")
                    # terminal_state remains "player_hub"
                else:
                    print("Player retirement canceled. Returning to player hub. \n")
                    # terminal_state remains "player_hub"

        elif terminal_action == "L":
            # terminal_state remains "player hub"
            log_game(player)

        elif terminal_action == "D":
            # terminal_state remains "player hub"
            delete_game(player)

        elif terminal_action == "R":
            display_game(player)
            terminal_state = "game lookup"

        elif terminal_action == "S":
            display_season(player)
            # terminal_state remains "player hub"

        elif terminal_action == "H":
            terminal_state = "player hub"

    save_data(players)
    print("All changes saved. \n")

main()