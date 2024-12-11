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

# From the *Big Screen* to your everyday life
Movies and TV shows have always been a major influence in our daily, shaping our preceptions, preferences and even cultural norms. From political messages delivered through the narrative to the emergence of new slang expressions, the impact of this medium is powerful and often underrated. Over the years, actors and the characters they played have redefined societal behaviours, starting fashion trends and even ideologies. 

For example, the famous sitcom *Friends* created "The Rachel" phenomenon. In this show, the character played by Jenifer Aniston wore an original haircut that became one of the most requested styles at hair salons across the world. It symbolized a moment where people were identifying as Rachel, were marked by the show and wanted to be just like her. Which is just what we are looking for: media influence !

{% include rachel.html %}

The case illustrates how a single person's captivated the audience and shaped the tastes of thousands, displaying how far the power of storytelling and character design reaches. That effect is what intrigued us for our project and guided us toward its subject.
In this article, we will see how the character names in movies induce trends in baby names, particularly the years immediately following the movie release. 

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
{% include top_10_genres.html %}
**NB:** A movie can belong to multiple genres.


## The baby names collection
Even if it remains a simple word, your name is what you are referred as for your entire life. It represents your whole identity and often mirrors cultural trends, family traditions or historical events. A cultural event can even create a new name, as for [Anakin](https://en.wikipedia.org/wiki/Anakin_(given_name)) or [Neo](https://en.wikipedia.org/wiki/Neo_(The_Matrix)). 

We used a dataset consisting of baby names each year for the United States, United Kingdom, France and Denmark to acccount for name trends.
### Most given names in the dataset
<img src="assets/img/wordcloud.png" alt="Word Cloud">



# Test 2 colonnes de texte
<div class="two-col">
  <div>
    <p>Text a gauche lorem fidsfjiji j idfisi ii ii ifii ii fi i ifjwionfnenfo nn nef iewi omeiofm owmefiom io</p>
  </div>
  <div>
    <p>Paragraph on the right for additional content or details.</p>
  </div>
</div>


# Bibliography
1. [Wikipedia: The Rachel](https://en.wikipedia.org/wiki/The_Rachel)
2. [Rachel's Picture](https://tierneysalons.com/wp-content/uploads/2023/12/0e461a848663146e13e5444687934cb0.jpg)
3. [Article on "The Rachel" by InStyle](https://www.instyle.com/the-rachel-haircut-8575551)
4. [Header Background Picture](https://imgur.com/photo-103bn-photo-116-hollywood-stars-including-leonardo-di-caprio-steven-spielberg-tom-cruise-robert-downey-jr-jack-nicholson-sean-penn-brad-pitt-martin-scorsese-dustin-hoffman-meryl-streep-jj-abrams-barbra-streisand-more-pose-toge-w1z5c) 


