Feature: Picking things up
  As a player of the game, or a monster
  I want to be able to pick things up
  So that I can subsequently use them in the game

Background: A game is in progress
  Given the default test map

Scenario Outline: Pick up clothes
  Given a <thing> on the ground where the <actor> is standing
  And the <actor> is wearing nothing
  When the <thing> is picked up by the <actor>
  Then the <actor> is wearing the <thing>
  And nothing is on the ground where the <actor> is standing

Examples: Body slot items
  | actor    | thing      |
  | player   | lab coat   |
  | player   | ninja suit |

Scenario Outline: Pick up clothes whilst already wearing something (in the same slot)
  Given a <thing> on the ground where the <actor> is standing
  And the <actor> is wearing the <other thing>
  When the <thing> is picked up by the <actor>
  Then the <actor> is wearing the <thing>
  And the <other thing> is on the ground where the <actor> is standing

Examples: Body slot items
  | actor    | thing      | other thing |
  | player   | lab coat   | ninja suit  |
  | player   | ninja suit | lab coat    |

Examples: Head slot items
  | actor    | thing          | other thing  |
  | player   | xray specs     | infra specs  |
  | player   | torch helmet   | xray specs   |
  | player   | analysis specs | torch helmet |

Scenario Outline: Drop the clothes being worn
  Given the <actor> is wearing a <thing>
  When the <thing> is dropped by the <actor>
  Then the <actor> is wearing nothing

Examples: Body slot items
  | actor    | thing      |
  | player   | lab coat   |
  | player   | ninja suit |
