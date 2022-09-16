from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
import random

# ------------------------ game logic (objects)---------------------------------------------

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
    
    def __repr__(self):
        return f"{self.value} of {self.suit}"

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()


class Deck:
    def __init__(self):
        suits = ["Hearts", "Diamonds", "Spades", "Clubs"]
        values = ["A", "2", "3", "4", "5", "6", "7" , '8','9','10','J','Q','K']
        self.cards = [Card(value, suit) for value in values for suit in suits]

    def __repr__(self):
        return f"Deck of {self.count()} cards"

    def count(self):
        return len(self.cards)
    
    def shuffle(self):
        random.shuffle(self.cards)

    def _reset_deck(self):
        self.__init__()
        self.shuffle()

    def _remove_cards(self, cards_list):
        for card in cards_list:
            self.cards.remove(card)

    def _deal(self, num_deal):
        cards_dealt = []

        for num in range(num_deal):
            if self.count() == 0:
                self._reset_deck()
                self._remove_cards(cards_dealt)
            
            if self.count() > 0:
                card_dealt = self.cards.pop(self.count()-1)
                cards_dealt.append(card_dealt)
            
        return cards_dealt

    def deal_card(self):
        return self._deal(1)

    def deal_hand(self, num_deal):
        return self._deal(num_deal)

class Player:
    def __init__(self):
        self.hand = []
        self.handvalue = 0

    def check_handvalue(self):
        handvalue = 0 
        aces  = 0
        for card in self.hand:
            if card.value == "J":
                handvalue += 10
            elif card.value == "Q":
                handvalue += 10
            elif card.value == "K":
                handvalue += 10
            elif card.value == "A":
                aces += 1
            else:
                handvalue += int(card.value)
        
        if aces > 0 :
            for num_aces in range(aces):
                if handvalue + 11 > 21:
                    handvalue += 1
                else:
                    handvalue +=11

        self.handvalue = handvalue

        return self.handvalue
        
class Dealer(Player): 
    def __init__(self):
        super().__init__()

        
class Game:
    def __init__(self):
        # initialize deck, player, and dealer
        self.deck = Deck()
        self.player = Player()
        self.dealer = Dealer()
        self.win = False
        self.lose = False

    def new_game(self):
        # shuffle deck
        self.deck.shuffle()
        # deal hands
        self.dealer.hand = self.deck.deal_hand(2)
        self.player.hand = self.deck.deal_hand(2)
        # calculate value of hands
        self.dealer.check_handvalue()
        self.player.check_handvalue()

    def stand(self):
        # dealer must take a card if hand value < 17, dealer must stand if hand value >= 17
        while self.dealer.handvalue < 17:
            self.dealer.hand.append(self.deck.deal_card()[0])
            self.dealer.check_handvalue()

        # dealer bust
        if self.dealer.handvalue > 21:
            self.win = True
            return self.win

        # compare dealer hand to player hand
        if self.dealer.handvalue >= self.player.handvalue:
            self.lose = True
            return self.lose
        else:
            self.win = True
            return self.win
    
    def hit(self):
        self.player.hand.append(self.deck.deal_card()[0])
        self.player.check_handvalue()

         # check if bust
        if self.player.handvalue > 21:
            self.lose = True
            return self.lose
        
        self.bust = False
        return self.bust


# ---------------------------- APIs -------------------------------------

app = Flask(__name__)
api = Api(app)
CORS(app)

@app.route('/')
def home():
    return "Website content"

class Start(Resource):
    def post(self):
        global game
        game = Game()
        game.new_game()

        return {
            "dealerHand": [str(card) for card in game.dealer.hand],
            "playerHand": [str(card) for card in game.player.hand]
        }
    
api.add_resource(Start, "/start")

class Hit(Resource):
    def post(self):
        game.hit()
        return {
            "bust": game.lose,
            "playerHand": [str(card) for card in game.player.hand]
        }

api.add_resource(Hit, "/hit")

class Stand(Resource):
    def post(self):
        game.stand()
        if game.win:
            return {
                "dealerHand": [str(card) for card in game.dealer.hand],
                "win": game.win,
                "lose": False
            }
        else:
            return {
                "dealerHand": [str(card) for card in game.dealer.hand],
                "win": False,
                "lose": game.lose
            }

api.add_resource(Stand, "/stand")

class Test(Resource):
    def get(self):
        return {"card": ["Ace of Hearts", "2 of Spades", "3 of Clubs"] }
    
    def post(self):
        return {"data": "posted"}

api.add_resource(Test, "/test")


if __name__ == '__main__':
    app.run(debug=True)



    


