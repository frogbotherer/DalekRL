Feature: A ninja suit
  As a player of the game
  I want to be able to wear a ninja suit
  So that I can hide in the shadows more easily

Background: A game is in progress
  Given the default test map

Scenario: Pick up a ninja suit
  Given a ninja suit on the ground where the player is standing
  And the player is wearing nothing
  When the ninja suit is picked up by the player
  Then the player is wearing the ninja suit
  And nothing is on the ground where the player is standing
  And the player has the hidden in shadow effect

Scenario: Drop the ninja suit being worn
  Given the player is wearing a ninja suit
  When the ninja suit is dropped by the player
  Then the player is wearing nothing
  And the ninja suit is on the ground where the player is standing
  And the player does not have the hidden in shadow effect

Scenario: Can't be seen in shadows
  Given the player is wearing a ninja suit
  And a dim light level
  And a static camera enemy near the player
  When turns are taken
  Then the static camera is not alerted to the player

Scenario: Can still be seen in bright light
  Given the player is wearing a ninja suit
  And a bright light level
  And a static camera enemy near the player
  When turns are taken
  Then the static camera is alerted to the player
