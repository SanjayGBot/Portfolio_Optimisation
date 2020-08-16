#importing necessary libraries
import yfinance as yf
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

import streamlit as st

#Hiding details of streamlit
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


#Heading 
st.markdown("<h2 style='text-align: center; color: black;'>Effective Portfolio Selection by Monte Carlo Simulation</h2>", unsafe_allow_html=True)
st.text('')
st.markdown("<h3 style='text-align: center; color: black;'>Only for cash segment(NSE) </h3>", unsafe_allow_html=True)

#getting past datas 
def past_data(symbol):
    symb = yf.Ticker(symbol+'.NS')
    
    data = symb.history(period='1y')

    return data

#Empty linespace
for i in range(5):
    st.text('')

#Inputs from user
user_input = st.text_input('Enter the symbols of stock to be added to the portfolio (separated by commas(","))',None)
num_portfolio = st.number_input('Enter the number of portfolios for simulation( ">=10,000")',min_value = 10000,format = '%i')

st.text('Press Submit button')
button = st.button('Submit')

st.markdown('*Note: Takes more time if number of stocks or number of portfolio is very large.*')
#Start of program
if button:

    symb_list = list(set(user_input.split(',')))

    if len(symb_list) <= 2:
        st.write('Please enter more than 2 stocks')
    else :    
        data_dict = dict()

        #Extracting past datas of given stocks
        for i in symb_list:
            data_dict[i.upper()] = past_data(i.upper())
        st.balloons()

        

        #Extracting Close Price of the stocks and creating a dataframe
        CP_dict = {}
        for key,val in data_dict.items():
            CP_dict[key] = val['Close']
        
        CP_df = pd.DataFrame(CP_dict)
        
        #Calculating log daily returns of stocks
        daily_returns = np.log(CP_df.pct_change() + 1).dropna()
    

        

        #Calculating mean returns and covariance of all stocks
        mean_returns = np.array(daily_returns.mean())
        cov = daily_returns.cov()
        
      

        #Monte Carlo Simulation
        if num_portfolio < 10000:
            st.write('Enter a number greater than 10K')
        else:
        
            results = np.zeros((3 + len(daily_returns.columns),num_portfolio))

            for i in range(num_portfolio):
                weights = np.random.rand(len(daily_returns.columns))
                weights = weights/np.sum(weights)

                p_annual_return = np.sum(weights * mean_returns) * 252
                p_annual_volatility = np.sqrt(np.dot(weights.T,np.dot(cov,weights))) * np.sqrt(252)

                results[0,i] = p_annual_return
                results[1,i] = p_annual_volatility
                results[2,i] = results[0,i]/results[1,i]

                for j in range(len(weights)):
                    results[j+3,i] =  weights[j]


            cols = ['Ann_Ret','Ann_Vol','Sharpe_Ratio']
            for num in range(len(list(daily_returns.columns))):
                cols.append(list(daily_returns.columns)[num])
            
            result_df = pd.DataFrame(results.T,columns=cols)
            
            #locating the 
            #Portfolio 1 - Sharpe ratio is the highest
            #Portfolio 2 - Volatility is the lowest
            

            #Portfolio 1
            max_sharpe_ratio = result_df.iloc[result_df['Sharpe_Ratio'].idxmax()]

            #Portfolio 2
            volatility_lowest = result_df.iloc[result_df['Ann_Vol'].idxmin()]


            #Plotting the simulation
            
            plt.scatter(result_df['Ann_Vol'],result_df['Ann_Ret'],c =result_df['Sharpe_Ratio'],cmap='RdYlBu')
            plt.colorbar()

            plt.scatter(max_sharpe_ratio[1],max_sharpe_ratio[0],marker = (5,1,3),color='red',s=700) #red - Portfolio 1
            plt.scatter(volatility_lowest[1],volatility_lowest[0],marker = (5,1,3),color='green',s=700)#Green - Portfolio 2
            

            plt.xlabel('Volatility')
            plt.ylabel('Returns')
             

            st.pyplot() 

            #Max_Sharpe_Ratio
            st.markdown('Max Sharpe Ratio Portfolio Allocation :sunglasses:')
            st.write(round(max_sharpe_ratio * 100,2))

            #Least_Voaltility
            st.markdown('Least Volatile Portfolio Allocation :innocent:')
            st.write(round(volatility_lowest * 100,2))

            st.write('**Note : **  *All values above are in %*')
