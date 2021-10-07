# crypto
## Funding Rates Plotting
* Create virtual env
* pip install -r requirements 
* Config in exchange_config.py
    * API credentials
    * list of currencies
 * python funding_rates_plot.py

![GitHub Logo](./example.png)

Deployed in AWS Lambda running on an hourly CloudWatch scheduled event
https://crypto-plot.s3.amazonaws.com/crypto-plot-lambda.html
