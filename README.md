<a id="readme-top"></a>
<!-- PROJECT LOGO -->
<div align="center">
  <a href="https://github.com/abdullah72005/Stock_Trading">
  </a>
<h1 align="center">Stock_Trading</h1>
  <p align="center">
    Stock_Trading is a Django web-based application designed to provide a realistic stock trading simulation experience. Users can register, manage their virtual portfolio, and fetch real-time stock prices using the Alpha Vantage API. The application emphasizes security, with features like password constraints, account balance management, and the ability to update passwords.
    <br />
    <a href="https://github.com/abdullah72005/Stock_Trading"><strong>Explore the docs »</strong></a>
  </p>
</div>



### Built With


* [![Python][Python-logo]][Python-url]
* [![Django][Django-logo]][Django-url]
* [![SQLite][SQLite-logo]][SQLite-url]
* [![HTML][HTML-logo]][HTML-url]
* [![CSS][CSS-logo]][CSS-url]
* [![JavaScript][JavaScript-logo]][JavaScript-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Features

- **User Authentication:**
  - Secure registration and login.
  - Password constraints for enhanced security.
  - Ability to change password.

- **Portfolio Management:**
  - Monitor current stock holdings and available cash balance.
  - Display total portfolio value with a breakdown of stock prices and quantities.

- **Stock Trading:**
  - Real-time stock prices fetched using the Alpha Vantage API.
  - Buy and sell shares with automatic balance and stock quantity validation.

- **Transaction History:**
  - Record of all transactions with timestamps for user reference.

- **Balance Management:**
  - Add or withdraw virtual cash to manage portfolio effectively.



<!-- GETTING STARTED -->
## Getting Started



### Prerequisites

Before you begin, make sure you have Python3 installed. Then,
<br>

* Install project dependencies:
  ```sh
  pip3 install -r requirements.txt
  ```

* Get an API Key from Alpha Vantage and add the key to a `.env` file in the root directory:
  ```env
  API_KEY=your_api_key_here
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/abdullah72005/Stock_Trading.git
   cd Stock_Trading
   ```
2. Apply database migrations
   ```sh
   python3 manage.py migrate
   ```
3. To start the application, execute:
   ```sh
   python3 manage.py runserver
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[Python-logo]: https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Django-logo]: https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white  
[SQLite-logo]: https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white  
[Django-url]: https://www.djangoproject.com/  
[SQLite-url]: https://sqlite.org/  
[CSS-logo]: https://img.shields.io/badge/CSS-1572B6?style=for-the-badge&logo=css3&logoColor=white
[CSS-url]: https://www.w3.org/Style/CSS/
[JavaScript-logo]: https://img.shields.io/badge/JavaScript-F7DF1C?style=for-the-badge&logo=javascript&logoColor=black
[JavaScript-url]: https://developer.mozilla.org/en-US/docs/Web/JavaScript
[HTML-logo]: https://img.shields.io/badge/HTML-E34F26?style=for-the-badge&logo=html5&logoColor=white
[HTML-url]: https://developer.mozilla.org/en-US/docs/Web/HTML
