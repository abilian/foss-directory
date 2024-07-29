Feature: Links

    Background:
        Given browser "Firefox"

    @web
    Scenario: Navigating through main menu
        When I go to home
        And I click the link with text "Wire"
        Then I should see "WIRES"

        When I click the link with text "WIP"
        Then I should see "Tableau de bord"

        When I click the link with text "Events"
        Then I should see "Evénements"

        When I click the link with text "Biz"
        Then I should see "Marketplace"

        When I click the link with text "Swork"
        Then I should see "Annuaire"
