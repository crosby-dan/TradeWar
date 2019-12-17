import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import GameFunctions

class Changes:
    def __init__(self):
        """ Create a new point at the origin """
        self.Tariff = 0
        self.fairtrade = 0

def setup(intPlayers):
    #fast setup mode of 4 handed AI game
    if intPlayers==-1:
        intPlayers=3
        FastSetup='4AI'
    elif intPlayers==-2:
        intPlayers=2
        FastSetup='Dan2'
    else:
        FastSetup=False

    # initialize list of countries and randomly sort it
    data = [['Canada',1653042795255, 432405190, 420631850, .0381, 'Justin Trudeau', 'Can we all just get along?'], ['USA',19390604000000,2407390189,1545609158,-.0033,'Donald Trump','Skeptical of Trade Deals'], ['China', 12237700479375, 1843792938,2263370504,.0243,'Xi Jinping', 'Aggressive'], ['Mexico', 1150887823404, 420369113, 409451378,.0329,'Andrés Obrador','Everything to lose']]
    dfCountries = pd.DataFrame(data, columns = ['Country', 'GDP', 'Imports', 'Exports', 'GrowthRate', 'President','AI']) 
    dfCountries = dfCountries.sample(frac=1).reset_index(drop=True)

    for currentPlayer in range(1, intPlayers+1, 1):
        #print("Player " + str(currentPlayer))
        if FastSetup=='Dan2' and currentPlayer==1:
            strType='H'
            strName='Dan'
        elif FastSetup=='Dan2' or FastSetup=='4AI':
            strType='A'
        else:
            print("** Will player " + str(currentPlayer) + " be (H)uman or (A)I? -->")
            strType=input()

        if not (strType).upper() in ('H','A'):
            print("Invalid player type, game cancelled.")
            sys.stdout.flush() 
            sys.exit(0)
        if (strType).upper()=='H' and not FastSetup:
            print("Player " + str(currentPlayer) + " - enter your name (or enter to cancel) -->")
            strName=input()
            if strName=="": 
                print("Game cancelled.")
                sys.stdout.flush() 
                sys.exit(0)
        if (strType).upper()=='A':
            strName=dfCountries.iloc[currentPlayer-1]['President']
            #print("Player " + str(currentPlayer) + " - assigned a name of " + strName)
        if currentPlayer==1:
            playerdata = [[strName,(strType).upper(),0]]
            dfPlayers = pd.DataFrame(playerdata, columns = ['PlayerName','PlayerType', 'Score']) 
        else:
            dfPlayers = dfPlayers.append(pd.Series([strName,(strType).upper(),0], index=dfPlayers.columns ), ignore_index=True)

    #Truncate countries list to the current number of players
    dfCountries = dfCountries.head(intPlayers)

    #Combine player and countries dataframes
    dfPlayers.insert(0, 'key', range(1, 1 + len(dfPlayers)))
    dfCountries.insert(0, 'key', range(1, 1 + len(dfCountries)))
    dfPlayers=dfPlayers.set_index('key').merge(dfCountries.set_index('key'), on='key', how='left')
    return dfPlayers

def calculateAIchanges(Name,OppPresident,MyTariff,OppTariff,MyFairTrade,OppFreeTrade,AIPersonality):
    c=Changes()
    if AIPersonality=="Everything to lose":
        #Note:  Everything to lose countries will not risk Tariffs or unfair trade, they will mainly just complain.
        #print("Using AI: Nothing to lose")
        if OppTariff>MyTariff: 
            print("   -->",Name,"sends sad letter to",OppPresident,"saying, 'Your Tariffs make us sad.'")
        elif OppFreeTrade<0: 
            print("   -->",Name,"sends sad letter to",OppPresident,"saying, 'Your trade policies make us sad.'")
        else:
            print("   -->",Name,"thanks",OppPresident,"for doing business.'")
    elif AIPersonality=="Can we all just get along?":
        #print("Using AI: Can we all just get along?")
        #Variables Available:  Name,OppPresident,MyTariff,OppTariff,MyFairTrade,OppFreeTrade,AIPersonality
        if OppFreeTrade<-2:
            print("   -->",Name,"tells",OppPresident,"Your trade policies are unfair, we are raising Tariffs.")
            c.Tariff=MyTariff+.1
        elif OppFreeTrade>-1 and OppTariff<=.2 and MyTariff>0:
            print("   -->",Name,"tells",OppPresident,"Thank you for trading more fairly, we are lowering Tariffs.")
            c.Tariff=MyTariff-.1
        elif OppTariff>0 and MyFairTrade<0:
            print("   -->",Name,"tells",OppPresident,"Ok Fine, we will ease our import restrictions, please lower your Tariffs.")
            c.fairtrade=c.fairtrade+1
        elif OppTariff>.1 and OppTariff>MyTariff:
            print("   -->",Name,"tells",OppPresident,"We are retaliating to your high Tariffs.")
            c.Tariff=MyTariff+.1
        elif MyFairTrade>-1:
            print("   -->",Name,"Legislates changes to limit imports.")
            c.fairtrade=MyFairTrade-1
        else:
            print("   -->",Name,"thanks",OppPresident,"for doing business.'")
    elif AIPersonality=="Aggressive":
        #print("Using AI: Aggressive")
        #Variables Available:  Name,OppPresident,MyTariff,OppTariff,MyFairTrade,OppFreeTrade,AIPersonality
        if OppFreeTrade<0:
            print("   -->",Name,"censors: ",OppPresident,"; your trade policies are unfair, we are raising Tariffs.")
            c.Tariff=MyTariff+.1
        elif OppFreeTrade>-2 and OppTariff<=.1 and MyTariff>0:
            print("   -->",Name,"praises",OppPresident,"; thank you for trading more fairly, we are lowering Tariffs.")
            c.Tariff=MyTariff-.1
        elif OppTariff>.2 and MyFairTrade<0:
            print("   -->",Name,"opines to",OppPresident,"; OK Fine, we will trade more fairly, please lower your Tariffs.")
            c.fairtrade=c.fairtrade+1
        elif OppTariff>.1 and OppTariff>MyTariff:
            print("   -->",Name,"Retaliates to ",OppPresident,"; we are retaliating to your high Tariffs.")
            c.Tariff=MyTariff+.1
        elif MyFairTrade>-2:
            print("   -->",Name,"secretly manipulates markets to create unfair trade advantage.")
            c.fairtrade=c.fairtrade-1
        else:
            print("   -->",Name,"thanks",OppPresident,"for doing business.'")
    elif AIPersonality=="Skeptical of Trade Deals":
        #print("Using AI: Skeptical")
        #Variables Available:  Name,OppPresident,MyTariff,OppTariff,MyFairTrade,OppFreeTrade,AIPersonality
        if OppFreeTrade<=-.2:
            print("   -->",Name,"tweets",OppPresident,"Your trade policies are unfair, we are raising Tariffs.")
            c.Tariff=MyTariff+.1
        elif OppFreeTrade>-2 and OppTariff<=.1 and MyTariff>0:
            print("   -->",Name,"tweets",OppPresident,"Thank you for trading more fairly, we are lowering Tariffs.")
            c.Tariff=MyTariff-.1
        elif OppTariff>0 and MyFairTrade<0:
            print("   -->",Name,"tweets",OppPresident,"Ok Fine, we will trade more fairly, please lower your Tariffs.")
            c.fairtrade=c.fairtrade+1
        elif OppTariff>.1 and OppTariff>MyTariff:
            print("   -->",Name,"tweets",OppPresident,"We are retaliating to your high Tariffs.")
            c.Tariff=MyTariff+.1
        else:
            print("   -->",Name,"thanks",OppPresident,"for doing business.'")
    return c
