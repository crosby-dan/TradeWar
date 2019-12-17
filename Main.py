import sys
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import GameFunctions

print("Welcome to trade war!")
print("How many total players will there be (2 to 4)? -->")
intPlayers=int(input())
plotBoundLow=1
plotBoundHigh=1

if (intPlayers<2 or intPlayers>4) and not intPlayers<0:
    print("Invalid Player Count, Game cancelled.")
    sys.stdout.flush() 
    sys.exit(0)

#Default number of rounds
numRounds=3

if not intPlayers<0:
    print("How many rounds to play (press Enter for ", numRounds,") -->")
    strRounds=input()
    if strRounds.isnumeric():
        numRounds=int(strRounds)

if not (numRounds>0 and numRounds<101):
    numRounds=5

print("Playing ",numRounds," rounds (1 year each).")

dfPlayers=GameFunctions.setup(intPlayers)
if intPlayers==-1: 
    intPlayers=4

print(dfPlayers)
print("Press enter to begin round/year 1.")
strInput=input()

# Setup initial values for Tariffs
First=True
for row1 in dfPlayers.itertuples(index=True, name='Pandas'):
    for row2 in dfPlayers.itertuples(index=True, name='Pandas'):
        if row1.Index!=row2.Index:
            #Default fair trade value, -5 is really bad, +5 is really good
            #Negative fair trade values will increase trade beyond what can happen with eliminating Tariffs
            #However, this advantage may cause retaliation
            FairTrade=0
            #print ("Setting initial Tariff",row1.PlayerName,' vs ', row2.PlayerName)
            if row1.Country=="China": FairTrade=-3
            if row1.Country=="Mexico": FairTrade=-1
            Tariff=0.0
            TradeChange=1
            LogEntry="Initial Value Setup"
            if First:
                TradeData = [[row1.Index,row2.Index,0,FairTrade,Tariff,TradeChange,LogEntry]]
                dfTradeInfo = pd.DataFrame(TradeData, columns = ['Player1','Player2', 'Round', 'FairTrade', 'Tariff', 'TradeChange', 'LogEntry']) 
                #dfTradeInfo.set_index(['Player1','Player2', 'Round'], inplace=True)
                First=False
            else:
                TradeData = [row1.Index,row2.Index,0,FairTrade,Tariff,TradeChange,LogEntry]
                dfTradeInfo = dfTradeInfo.append(pd.Series(TradeData, index=dfTradeInfo.columns ), ignore_index=True)

#Main game play loop for each round
for currentRound in range(1,numRounds+1):
    #For each round, loop through each player.
    First=True
    for player in dfPlayers.itertuples(index=True, name='Pandas'):
        #Loop through each opposing player and do calculations
        if player.PlayerType=="H":
            print("*** Year {0}, {1} President {2} ***".format(currentRound,player.Country,player.President))
        else:
            print("*** Year {0}, {1} President {2} AI: {3} ***".format(currentRound,player.Country,player.President,player.AI))
        print("******************************************************************")

        for MyTradePolicy in dfTradeInfo.query('Player1==' + str(player.Index) + ' and Round==' + str(currentRound-1)).itertuples(index=True, name='Pandas'):
            #Get opponent player dataframe
            oppCountry=dfPlayers[dfPlayers.index==MyTradePolicy.Player2].iloc[0]['Country']
            oppPlayerName=dfPlayers[dfPlayers.index==MyTradePolicy.Player2].iloc[0]['PlayerName']
            output="{0:10} vs. {1:10}: ".format(player.Country,oppCountry)
            #we need to get the values for the opponents competing trade treatments
            #NOTE:  Programming comment - there is only going to be one row in this dataset, but this seemed to be the fastest way of providing access to all the values returned by this query.
            for OppTradePolicy in dfTradeInfo.query('Player1==' + str(MyTradePolicy.Player2) + ' and Player2==' + str(player.Index) + ' and Round==' + str(currentRound-1)).itertuples(index=True, name='Pandas'):
                #Print current competition status
                output=output+" Tariff:    {0:3.0%} <=> {1:3.0%} ".format(MyTradePolicy.Tariff,OppTradePolicy.Tariff)
                output=output+" Fair Trade: {0:3}   <=> {1:3}   ".format(MyTradePolicy.FairTrade,OppTradePolicy.FairTrade)
                output=output+" Trade:      {0:3.1%} <=> {1:3.1%} ".format(MyTradePolicy.TradeChange,OppTradePolicy.TradeChange)
                print(output)

                NewTariff=MyTradePolicy.Tariff
                NewFairTrade=MyTradePolicy.FairTrade

                if player.PlayerType=="H":
                    print("Do you wish to change your current Tariff or Trade Policy?  (1=Increase Tarrif, 2=Decrease Tariff, 3=Improve Fair Trade, 4=Decrease Fair Trade, 0=No changes) -->")
                    userInput=input().upper()
                    while userInput not in ('0'):
                        if userInput not in ('1','2','3','4','Q'):
                            print("Invalid value.  (1=Increase Tarrif, 2=Decrease Tariff, 3=Improve Fair Trade, 4=Decrease Fair Trade, 0=No changes, Q=Quit Game)")
                            userInput=input().upper()
                        if userInput=="Q":
                            sys.stdout.flush() 
                            sys.exit(0)
                        if userInput=="1":
                            NewTariff=NewTariff+.1
                            print("{0}'s Tariff's for {1} increased to {2:3.1%}".format(player.Country,oppCountry,NewTariff))
                        if userInput=="2":
                            NewTariff=NewTariff-.1
                            print("{0}'s Tariff's for {1} decreased to {2:3.1%}".format(player.Country,oppCountry,NewTariff))
                        if userInput=="3":
                            NewFairTrade=NewFairTrade+1
                            print("{0}'s Fair Trade Policy for {1} increased to {2}".format(player.Country,oppCountry,NewFairTrade))
                        if userInput=="4":
                            NewFairTrade=NewFairTrade-1
                            print("{0}'s Fair Trade Policy for {1} decreased to {2}".format(player.Country,oppCountry,NewFairTrade))
                        userInput=input().upper()
                else:
                    #print("--- AI Round ",currentRound," for ",player.PlayerName, ", ", player.Country, ":")
                    Result=GameFunctions.calculateAIchanges(player.PlayerName,oppPlayerName,MyTradePolicy.Tariff,OppTradePolicy.Tariff,MyTradePolicy.FairTrade,OppTradePolicy.FairTrade,player.AI)
                    NewTariff=MyTradePolicy.Tariff+Result.Tariff
                    NewFairTrade=MyTradePolicy.FairTrade+Result.fairtrade
                #print("Saving: ",MyTradePolicy.Player1,MyTradePolicy.Player2)
                LogEntry=""
                if First:
                    TradeData = [[MyTradePolicy.Player1,MyTradePolicy.Player2,currentRound,NewFairTrade,NewTariff,0,LogEntry]]
                    dfTradeInfoTemp = pd.DataFrame(TradeData, columns = ['Player1','Player2', 'Round', 'FairTrade', 'Tariff', 'TradeChange', 'LogEntry']) 
                    First=False
                else:
                    TradeData = [MyTradePolicy.Player1,MyTradePolicy.Player2,currentRound,NewFairTrade,NewTariff,0,LogEntry]
                    dfTradeInfoTemp = dfTradeInfoTemp.append(pd.Series(TradeData, index=dfTradeInfo.columns ), ignore_index=True)

        print("******************************************************************")
        print("End of turn",currentRound," for ",player.Country,", press enter to continue or Q to quit-->")
        if input().upper()=="Q":
            sys.stdout.flush() 
            sys.exit(0)

    #Calculate a global trade growth number
    GlobalTrade=(random.randrange(980,1060,1)/1000)-1.0
    print ("Global trade changed this year by {0:2.1%}".format(GlobalTrade))
    print("End of round", currentRound,", press enter to view round results (or Q to quit)-->")
    if input().upper()=="Q":
        sys.stdout.flush() 
        sys.exit(0)

    #Calculate round results
    for player in dfPlayers.itertuples(index=True, name='Pandas'):
        #Loop through each opposing player and do calculations
        if player.PlayerType=="H":
            print("*** Year {0}, {1} President {2} ***".format(currentRound,player.Country,player.President))
        else:
            print("*** Year {0}, {1} President {2} AI: {3} ***".format(currentRound,player.Country,player.President,player.AI))
        #print("******************************************************************")
        for MyTradePolicy in dfTradeInfo.query('Player1==' + str(player.Index) + ' and Round==' + str(currentRound-1)).itertuples(index=True, name='Pandas'):
            #Get opponent player dataframe
            oppCountry=dfPlayers[dfPlayers.index==MyTradePolicy.Player2].iloc[0]['Country']
            oppPlayerName=dfPlayers[dfPlayers.index==MyTradePolicy.Player2].iloc[0]['PlayerName']
            PreviousTrade=MyTradePolicy.TradeChange
            #Get values for current year Tariff & trade decisions, inbound and outbound
            MyTariff=0
            MyFairTrade=0
            OppTariff=0
            OppFairTrade=0
            for MyTradePolicyNew in dfTradeInfoTemp.query('Player1==' + str(player.Index) + ' and Player2==' + str(MyTradePolicy.Player2) + ' and Round==' + str(currentRound)).itertuples(index=True, name='Pandas'):
                MyTariff=MyTradePolicyNew.Tariff
                MyFairTrade=MyTradePolicyNew.FairTrade
            for OppTradePolicyNew in dfTradeInfoTemp.query('Player1==' + str(MyTradePolicy.Player2) + ' and Player2==' + str(player.Index) + ' and Round==' + str(currentRound)).itertuples(index=True, name='Pandas'):
                OppTariff=OppTradePolicyNew.Tariff
                OppFairTrade=OppTradePolicyNew.FairTrade

            #Update calculated values
            #Assuming that a 10% Tariff assigned by ones own country has a 2.5% reduction to trade.
            NewTrade=PreviousTrade*(1-(MyTariff/12))
            #Assuming that a 10% Tariff assigned by other other country has a 3.33% reduction to trade.
            NewTrade=NewTrade*(1-(OppTariff/9))
            #Assuming that a -1 unfair trade advantage boosts trade by 1%
            NewTrade=NewTrade*(1-((MyFairTrade)*.01))
            #Assuming that a -1 unfair trade by the oppenent reduces trade benefit by 5%
            NewTrade=NewTrade*(1-((OppFairTrade)*-.008))
            #Multiplying by the global change
            NewTrade=NewTrade*(1+GlobalTrade)

            #Update chart axis min/max values as the values broaden
            if NewTrade<=plotBoundLow:
                plotBoundLow=NewTrade-.1
            if NewTrade>=plotBoundHigh:
                plotBoundHigh=NewTrade+.1

            #Save the round data            
            #TradeData = [MyTradePolicy.Player1,MyTradePolicy.Player2,currentRound,NewFairTrade,NewTariff,NewTrade,LogEntry]
            TradeData = [MyTradePolicy.Player1,MyTradePolicy.Player2,currentRound,MyFairTrade,MyTariff,NewTrade,LogEntry]
            dfTradeInfo = dfTradeInfo.append(pd.Series(TradeData, index=dfTradeInfo.columns ), ignore_index=True)

            #Display summary results
            output="{0:10}  vs.  {1:10}: Percent of Trade: {2:3.1%} ".format(player.Country,oppCountry,NewTrade)
            print(output)

    plt.figure()
    plt.subplots_adjust(hspace=.5)
    for player in dfPlayers.itertuples(index=True, name='Pandas'):
        #x=x+1
        for player2 in dfPlayers.itertuples(index=True, name='Pandas'):
            if player.Index != player2.Index:
                strLabel="Trade with " + player2.Country
                Data=dfTradeInfo.query('Player1==' + str(player.Index) + ' and Player2==' + str(player2.Index))
                if player.Index==1:
                    ax1 = plt.subplot(2,2,1)
                    ax1.xaxis.set_label_text("#1")
                    ax1.set_title(player.PlayerName + " of " + player.Country)
                    ax1.set_ylim([plotBoundLow,plotBoundHigh])
                    ax1.set_xticks(np.arange(0, currentRound+1, step=1))
                    dfTradeInfo.query('Player1==' + str(player.Index) + ' and Player2==' + str(player2.Index)).plot(kind='line',x='Round',y='TradeChange',ax=ax1,label=strLabel)
                elif player.Index==2:
                    ax2 = plt.subplot(2,2,2)
                    ax2.xaxis.set_label_text("#2")
                    ax2.set_title(player.PlayerName + " of " + player.Country)
                    ax2.set_ylim([plotBoundLow,plotBoundHigh])
                    ax2.set_xticks(np.arange(0, currentRound+1, step=1))
                    dfTradeInfo.query('Player1==' + str(player.Index) + ' and Player2==' + str(player2.Index)).plot(kind='line',x='Round',y='TradeChange',ax=ax2,label=strLabel)
                elif player.Index==3:
                    ax3 = plt.subplot(2,2,3)
                    ax3.xaxis.set_label_text("#3")
                    ax3.set_title(player.PlayerName + " of " + player.Country)
                    ax3.set_ylim([plotBoundLow,plotBoundHigh])
                    ax3.set_xticks(np.arange(0, currentRound+1, step=1))
                    dfTradeInfo.query('Player1==' + str(player.Index) + ' and Player2==' + str(player2.Index)).plot(kind='line',x='Round',y='TradeChange',ax=ax3,label=strLabel)
                elif player.Index==4:
                    ax4 = plt.subplot(2,2,4)
                    ax4.xaxis.set_label_text("#4")
                    ax4.set_title(player.PlayerName + " of " + player.Country)
                    ax4.set_ylim([plotBoundLow,plotBoundHigh])
                    ax4.set_xticks(np.arange(0, currentRound+1, step=1))
                    dfTradeInfo.query('Player1==' + str(player.Index) + ' and Player2==' + str(player2.Index)).plot(kind='line',x='Round',y='TradeChange',ax=ax4,label=strLabel)
    plt.xlabel("Year")
    plt.ylabel("Trade")
    plt.ylim([plotBoundLow,plotBoundHigh])
    plt.show()

    if input().upper()=="Q":
        sys.stdout.flush() 
        sys.exit(0)

