<div id="top"></div>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GNU General Public License v3.0][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">char level seq2seq machine translation on named entities</h3>

  <p align="left">
    character level machine translation on named entities, using fastapi, spacy, pytorch sequence 2 sequence model and docker
  </p>
  <p align="center">
    <a href="https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker/issues">Report Bug</a>
    ·
    <a href="https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#setup-superuser">Setup superuser</a></li>
        <li><a href="#upgrade-database-model">Upgrade Database Model</a></li>
        <li><a href="#deployement">Deployement</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
       <ul>
        <li><a href="#users">Users</a></li>
        <li><a href="#named-entities-recognition">Named Entities Recognition</a></li>
        <li><a href="#translations">translations</a></li>
      </ul>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

### Main goals

Use this project to easily setup a machine translation api for authenticated user.
Get 'normalized' entiites from a raw text (email, files, chatbot conversations): 
1. Add your own translation in database,
1. Crain your models using your translation pairs
1. Convert raw entities into actionnable features

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

* [FastAPI](https://fastapi.tiangolo.com/)
* [FastAPI users](https://fastapi-users.github.io/)
* [Pytorch](https://pytorch.org/)
* [Spacy](https://spacy.io/)
* [PostgreSQL](https://www.postgresql.org/)
* [Nginx](https://www.nginx.com/)
* [Docker](https://www.docker.com/)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started


### Prerequisites

* Install Docker and Docker-Compose

### Installation

* Clone the repo
  ```sh
  git clone https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker.git
  ```
* Build the docker image
  ```sh
  docker-compose build backend
  ```
* Setup keys and credentials in `.env`
  ```python
  POSTGRES_USER=db_user
  POSTGRES_PASSWORD=db_pass
  POSTGRES_DB=db_name
  SECRET_KEY=secret_key_for_users_management
  DATABASE_URL=postgres://db_user:db_pass@db:5432/db_name
  ```
* Add your own NER model, see [Spacy docs](https://spacy.io/usage/training)
* Run your containers
  ```sh
  docker-compose up -d;docker-compose logs -f
  ```
* Init you database
  ```sh
  docker-compose exec backend aerich init-db
  ```
* Add your dataset files and train your own seq2seq model
  ```sh
  docker-compose exec backend python app/services/training.py
  ```
  * Run tests
  ```sh
  docker-compose exec backend pytest
  ```

### Setup superuser
* Access DB cmd line
  ```sh
  docker exec -it mt_db psql -U db_user -h 127.0.0.1 -W db_name
  ```
* Grant superuser rigths
  ```sh
  UPDATE usermodel SET is_superuser = 't', is_verified = 't' WHERE email = 'superuser@domain.com';
  ```

### Upgrade Database Model
* Generate migration file
  ```sh
  docker-compose exec backend aerich migrate
  ```
* Apply upgrade to DB
  ```sh
  docker-compose exec backend aerich upgrade
  ```

### Deployement

* Replace /config/nginx/nginx.conf with nginx.conf.live and update server_name refs
  ```sh
  server_name subdomain.domain.com;
  ```
* Add CAA record in your DNS
  ```sh
  sudomain.domain.com. CAA 0 issue letsencrypt.org
  ```
* Update refs in letsencrypt.sh
  ```sh
  domains=(subdomain.domain.com)
  email="contact@domain.com"
  ```
* Run letsencrypt.sh script to setup certificates
  ```sh
  sudo ./init-letsencrypt.sh
  ```


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

### Users

Using [FastAPIUsers](https://fastapi-users.github.io/fastapi-users/usage/flow/)

#### Registering

    curl \
        -H "Content-Type: application/json" \
        -X POST \
        -d "{\"email\": \"paul@domain.com\",\"password\": \"strongpassword\"}" \
        http://localhost/auth/register

Returns:

```json
{
    "id":"800e9564-6804-4ab5-bc59-a088182227be",
    "email":"paul@domain.com",
    "is_active":true,
    "is_superuser":false,
    "is_verified":false
}
```

#### Login

    curl \
        -H "Content-Type: multipart/form-data" \
        -X POST \
        -F "username=paul@domain.com" \
        -F "password=strongpassword" \
        http://localhost:8000/auth/login

Returns:

```json
{
    "access_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiODAwZTk1NjQtNjgwNC00YWI1LWJjNTktYTA4ODE4MjIyN2JlIiwiYXVkIjpbImZhc3RhcGktdXNlcnM6YXV0aCJdLCJleHAiOjE2MzAxMzk5OTJ9.w-ZWpm51fyybFivmKjun3qbXuqwXCgYyxGbPD1yhIr4",
    "token_type":"bearer"
}
```
### Named Entities Recognition

#### Get entities from text

curl -X 'POST' \
  'http://localhost/ner' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer token' \
  -H 'Content-Type: application/json' \
  -d '{
  "sentence": "un devis pour 500 flyers en quadri r/v, format a4 pour demain svp"
}'


Returns:

```json
{
  "entities": [
    {
      "text": "500",
      "entity": "EXEMPLAIRES",
      "pos": 0,
      "start": 14,
      "end": 17
    },
    {
      "text": "flyers",
      "entity": "PRODUCT",
      "pos": 1,
      "start": 18,
      "end": 24
    },
    {
      "text": "quadri r/v",
      "entity": "IMPRESSION",
      "pos": 2,
      "start": 28,
      "end": 38
    },
    {
      "text": "format a4",
      "entity": "FORMAT",
      "pos": 3,
      "start": 40,
      "end": 49
    }
  ],
  "ner": "imprimeur_4.3.20210312124255"
}
```


### Translations

#### Add a translation pair to your training dataset

curl -X 'POST' \
  'http://localhost/products' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer token' \
  -H 'Content-Type: application/json' \
  -d '{
  "entity_type": "FO",
  "source": "fo a4",
  "translation": "format ouvert : 210.0 x 297.0 mm"
}'


Returns:

```json
{
  "id": 2,
  "entity_type": "FO",
  "source": "fo a4",
  "translation": "format ouvert : 210.0 x 297.0 mm"
}
```

#### Export your training seq2seq training dataset (user must be "verified")

curl -X 'POST' \
  'http://localhost/products/extract' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer token' \
  -d ''

Returns:

```json
{
  "msg": "extracting"
}
```

#### Translate text entities

curl -X 'POST' \
  'http://localhost/translate' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer token' \
  -H 'Content-Type: application/json' \
  -d '{
  "entities": [
    {
      "text": "500",
      "entity": "EXEMPLAIRES",
      "pos": 0,
      "start": 14,
      "end": 17
    },
    {
      "text": "flyers",
      "entity": "PRODUCT",
      "pos": 1,
      "start": 18,
      "end": 24
    },
    {
      "text": "quadri r/v",
      "entity": "IMPRESSION",
      "pos": 2,
      "start": 28,
      "end": 38
    },
    {
      "text": "format a4",
      "entity": "FORMAT",
      "pos": 3,
      "start": 40,
      "end": 49
    }
  ],
  "model": "imprimeur"
}'

Returns:

```json
{
  "entities": [
    {
      "text": "500",
      "entity": "EXEMPLAIRES",
      "pos": 0,
      "start": 14,
      "end": 17
    },
    {
      "text": "flyers",
      "entity": "PRODUCT",
      "pos": 1,
      "start": 18,
      "end": 24
    },
    {
      "text": "recto : quadri, verso : quadri",
      "entity": "IMPRESSION",
      "pos": 2,
      "start": 28,
      "end": 38
    },
    {
      "text": "format fini : 210.0 x 297.0 mm",
      "entity": "FORMAT",
      "pos": 3,
      "start": 40,
      "end": 49
    }
  ]
}
```

_For more examples, please refer to the [Documentation](http://localhost/docs)_

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Train translation model with users dataset
    - [x] add translation pairs in DB
    - [x] extract dataset and train pytorch model
- [ ] User Verification by email
    - [ ] setup mailgun API Key
- [x] Named entity recognition to extract part of text to translate
    - [x] setup spay

See the [open issues](https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the GPL-3.0 License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Vincent PORTE - contact@neuralia.co

Project Link: [https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker](https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Pages](https://pages.github.com)
* [How To Install and Use Docker Compose on Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04)
* [Certificate Authority Authorization (CAA)](https://letsencrypt.org/docs/caa/)


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/vincentporte/machine_translation_fastapi_pytorch_docker.svg?style=for-the-badge
[contributors-url]: https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/vincentporte/machine_translation_fastapi_pytorch_docker.svg?style=for-the-badge
[forks-url]: https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker/network/members
[stars-shield]: https://img.shields.io/github/stars/vincentporte/machine_translation_fastapi_pytorch_docker.svg?style=for-the-badge
[stars-url]: https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker/stargazers
[issues-shield]: https://img.shields.io/github/issues/vincentporte/machine_translation_fastapi_pytorch_docker.svg?style=for-the-badge
[issues-url]: https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker/issues
[license-shield]: https://img.shields.io/github/license/vincentporte/machine_translation_fastapi_pytorch_docker.svg?style=for-the-badge
[license-url]: https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/vincentporte
[product-screenshot]: images/screenshot.png
