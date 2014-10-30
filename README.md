AWAP
====

Bot for Carnegie Mellon University Algorithms With a Purpose competition 2014. We were tasked with writing an AI to play a variant of the board game Blokus, which was then pitted against other AIs in a tournament-style format.

The folders cpp and java contain starter code in C++ and Java, respectively. We used the python starter code provided, modifying the find_move method to implement our AI.

We started out pretty simplistically, figuring that the game was small enough that we could try every single orientation of every single block in every single possible legal position and score it, and then choose the best scoring move. We scored it weighting it on how close the move would take us to the center, then based on whether or not it captured a doge tile, and then based on whether or not the corner of a block that we placed matched the corner of a block of another player (to sort of wall them off), and lastly based on whether or not a piece of the block to be placed fit in to a corner made by blocks of other players (to encourage moving into other player's territory). It was pretty simplistic, and we weren't quite able to iron out bugs in a more intelligent version that looked ahead two to three moves before making a move.

For more info, see http://acmalgo.com/
