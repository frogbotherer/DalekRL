Feature: A lab coat
  As a player of the game
  I want to be able to wear a lab coat
  So that I can feel more human
  (the real purpose is to provide a useless item that makes picking stuff up more risky)

Background: A game is in progress
  Given the default test map

Scenario: Pick up a lab coat
  Given a lab coat on the ground where the player is standing
  And the player is wearing nothing
  When the lab coat is picked up by the player
  Then the player is wearing the lab coat
  And nothing is on the ground where the player is standing

Scenario: Pick up a lab coat when already wearing something
  Given a lab coat on the ground where the player is standing
  And the player is wearing a ninja suit
  When the lab coat is picked up by the player
  Then the player is wearing the lab coat
  And the ninja suit is on the ground where the player is standing

Scenario: Drop the lab coat being worn
  Given the player is wearing a lab coat
  When the lab coat is dropped the player
  Then the player is wearing nothing
  And the lab coat is on the ground where the player is standing
