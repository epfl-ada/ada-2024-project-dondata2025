---
layout: page
title: Nice name! Where does it come from?
cover-img: 'assets/img/w1z5c.jpeg'
---

<link rel="stylesheet" href="assets/css/style.css">

<style>
    /*Custom css for the page*/
    .page-heading h1{
        background-color: rgba(190, 4, 4, 1);
    }
</style>

# From the *big screen* to your everyday life
Movies and TV shows have always been a major influence in our daily. From political messages to new slang expressions, there are numerous examples of actors or celebrities redefining how people behave, how they dress or even how they think. 

For example, the famous sitcom *Friends* created "The Rachel" phenomenon. In this show, the character played by Jenifer Aniston wore an original haircut that became one of the most requested ever.

{% include rachel.html %}

A single person's appearance managed to influence the tastes of thousands of people. This is what intrigued us for our project and lead us to its subject.
In this article, we will see how the character names in movies induce trends on baby names, particularly the few years following the movie release. 

# Try it yourself !
Before diving in deeper, let's give you a taste of our results. Enter any name, and see what movie potentially impacted its popularity.
{% include names_prediction.html %}

# Our *datasets* :
## The film corpus
First and most important, movies are what inspire people. They tell stories and affect our culture and lifestyle. For example, had you heard of macaws before [Rio](https://en.wikipedia.org/wiki/Rio_(2011_film)) ?

Our dataset contains movies released up to 2014 and informations such as their **unique ID**, **release date**, **genre** and the list of **characters** featured in the work.

In addition to that, we augmented it with [IMDB](https://www.imdb.com) **average rating** and **number of voters** coming from the [IMDB data files](https://datasets.imdbws.com).
### What makes a movie popular ?
Obviously, a blockbuster is more prone to impacting baby name trends than an obscure short film from the 40s. As such, we used the average IMDB rating of a movie as its popularity, excluding movies with few votes. 
### Genre representation
{% include top10_genres.html %}
**NB:** We grouped all genres that represent <1% of the dataset in "Other"



## The baby names collection
Even if it remains a simple word, your name is what you are referred as for your entire life. It represents your whole identity




# The influence of movies over your name
Your name is the word that is used to identify your person among others and has such
## Following part
<div class="two-col">
  <div>
    <p>Text a gauche lorem fidsfjiji j idfisi ii ii ifii ii fi i ifjwionfnenfo nn nef iewi omeiofm owmefiom io</p>
  </div>
  <div>
    <p>Paragraph on the right for additional content or details.</p>
  </div>
</div>


# Bibliography
1. [Wikipedia: The Rachel](https://en.wikipedia.org/wiki/The_Rachel#:~:text=%22The%20Rachel%22%20is%20described%20as,as%20the%20hairstyle's%20defining%20characteristics.)
2. [Rachel's Picture](https://tierneysalons.com/wp-content/uploads/2023/12/0e461a848663146e13e5444687934cb0.jpg)
3. [Header Background Picture](https://imgur.com/photo-103bn-photo-116-hollywood-stars-including-leonardo-di-caprio-steven-spielberg-tom-cruise-robert-downey-jr-jack-nicholson-sean-penn-brad-pitt-martin-scorsese-dustin-hoffman-meryl-streep-jj-abrams-barbra-streisand-more-pose-toge-w1z5c) 


