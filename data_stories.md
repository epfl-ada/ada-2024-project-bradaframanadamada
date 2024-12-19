---
layout: default
title: Data Story
permalink: /
---

# What characteristics make an actor’s career successful ?

## Are the founded personas relevant ? Relationship between a persona and the character occupation played by an actor in a movie


<div style="display:flex; align-items: center;">
    <p style="flex: 1; text-align: justify">
        We have extracted only a relatively small proportion of occupations per characters originally. As a result, 
        this part doesn't represent a major part of our analysis. However, they provide an interesting opportunity 
        to validate the personas previously extracted using an LLM. By linking characters' occupations to their 
        assigned personas, we can evaluate the relevance of the personas extracted from film summaries by comparing 
        them to the occupations list of the characters. We can also argue that the characters with a defined list of 
        occupations are likely the most popular, as the occupations list was retrieved from Wikidata. It is reasonable 
        to assume that only the more popular characters are documented on Wikidata.<br><br>
        Below, you can see an interactive bar chart displaying the distribution of the Top-20 most frequent character 
        occupations for each of the 12 personas defined in our analysis. You can use the picker located in the top-right 
        corner of the graph to select the persona for which you want to display the top 20 most common character occupations 
        associated with it.
    </p>
    <figure>
        <img src="src/image/persona_character_relation_chatGPT.jpg" width="350" height="200">
        <figcaption style="text-align: center"> Generated using AI</figcaption>
    </figure>
</div>

<iframe src="src/graphs/personas_characters_occupations_relations_graph_interactive.html" width="1200" height="800"></iframe>

<p style="flex: 1; text-align: justify">
    - The <b>warrior</b> persona is primarily linked to occupations such as <b>vigilante</b>, <b>swordfighter</b>, 
    <b>superhero</b>, <b>soldier</b>, <b>martial artist</b> and <b>private investigator</b>. These are common attributes 
    and professions associated with the <b>warrior</b> persona.<br><br>
    - The <b>rebel</b> persona, on the other hand, is more closely linked to darker occupations such as <b>serial killer</b>,
    <b>mass murderer</b>, <b>terrorist</b> and <b>spy</b>. However, it is also associated with more heroic professions like 
    <b>superhero</b>, <b>vigilante</b>, and <b>swordfighter</b>, which may represent anti-hero or versatile roles.<br><br>
    - The <b>joker</b> persona is most strongly linked to occupations like <b>handyman</b> and <b>swordfighter</b>, with 
    additional occupations that don't have a direct connection to humor. This makes it difficult to fully evaluate the 
    relevance of the <b>joker</b> persona affectation.<br><br>
    - The <b>caregiver</b> persona is also associated with occupations that are not directly linked to the healthcare 
    field. However, we can also define the <b>caregiver</b> persona has a character who assist the main character in his 
    quest. Occupations like <b>superhero</b>, <b>vigilante</b>, or <b>reporter</b> (in the case of police films) fit this 
    definition, as they represent occupations that often help the main characters in his quest.<br><br>
    - The <b>ruler</b> persona is associated with negative occupations like <b>terrorist</b>, <b>serial killer</b> and 
    <b>mass murderer</b>, which could align with the representation of a villainous leader commonly seen in films. It is 
    also linked to more traditional leadership roles such as <b>chief executive officer</b>, <b>ruler</b>, <b>crime boss</b> 
    or <b>monarch</b>.<br><br>
    - The <b>mentor</b> persona is strongly associated with occupations that play significant roles in the storyline, such 
    as <b>private investigator</b>, <b>vigilante</b>, <b>martial artist</b>, <b>detective</b> and <b>superhero</b>. This 
    makes sense, as the <b>mentor</b> persona often holds an important position in the narrative, who is guiding or forming 
    another important character.<br><br>
    - The <b>lover</b> persona is linked to occupations like <b>high school student</b>, <b>reporter</b>, and <b>student</b>, 
    which are common in romantic films. It is also associated with dominant film roles such as <b>swordfighter</b>, <b>vigilante</b>, 
    <b>superhero</b> and <b>martial artist</b>, which complement the <b>lover</b> persona since these role represent 
    dominant characters.<br><br>
    - The <b>seducer</b> persona is associated with darker roles such as <b>serial killer</b> or <b>murderer</b>, explained 
    by the manipulative traits present in these roles, which is coherent with the <b>seducer</b> persona. It is also linked 
    to more dominant personas like <b>soldier</b>, <b>superhero</b>, and <b>actor</b>, which makes sense as these characters
    may represent desirable traits.<br><br>
    - The <b>magician</b> persona is connected to occupations like <b>magician</b>, <b>crime boss</b>, <b>alchemist</b> and
    <b>chemist</b>, highlighting the relevance of the persona's traits. In the same time, it is also associated with darker 
    occupations like <b>serial killer</b>, <b>criminal</b> and <b>terrorist</b>. This suggests that magicians are often 
    represented as characters with darker aspects.<br><br>
    - It is challenging to fully evaluate the relevance of the <b>orphan</b> persona, even it is linked to occupations like 
    <b>student</b> and <b>soldier</b> roles often performed by orphaned characters in movies.<br><br>
    - The <b>creator</b> persona is linked to a broad range of occupations, many of which are connected to the innovative 
    field, such as <b>inventor</b>, <b>scientist</b> and <b>writer</b>.
    - The <b>child</b> persona is predominantly associated with occupations like <b>schoolchild</b> and <b>student</b>, 
    which is appropriate for this role.<br><br>
    Overall, most personas show their relevance through this analysis, even though the <b>joker</b> persona is harder 
    to evaluate due to the lack of direct occupations linked to humor.<br><br>
</p>

## The Diversity in the actors occupations/professions. 
<div style="display:flex; align-items: center;">
    <p style="flex: 1; text-align: justify">
        An actor, in addition to their main profession, could have engaged in many other types of occupations 
        throughout their career. These complementary occupations can provide an interesting perspective on the 
        actor's skills. Comparing the occupations an actor has pursued with the different personas they have performed 
        along his career can offer an overview of the skills and qualities required to act a given persona.<br><br>
        Below, you can see a bar chart highlighting the distribution of the top 20 most common occupations across 
        the 12 personas defined earlier in our analysis. You can use the picker located in the top-right corner of the 
        graph to select the persona for which you want to display the top 20 most common actor occupations associated 
        with it. For this visualization, we exclude actor's occupations "actor", "film actor" and "television actor", as 
        they are very closed to the core profession of acting. 
    </p>
    <figure>
        <img src="src/image/actor_diversity_occupation_chatGPT.png" alt="actor_profession_diversity" width="350" height="200">
        <figcaption style="text-align: center"> Actor Professions/Occupations Diversity: Generated using AI</figcaption>
    </figure>
</div>

<iframe src="src/graphs/personas_actors_occupations_relations_graph_interactive.html" width="1200" height="800"></iframe>

<p style="flex: 1; text-align: justify">
    The personas <b>the orphan</b>, <b>the ruler</b>, <b>the warrior</b>, <b>the seducer</b>, <b>the lover</b>, 
    <b>the mentor</b>, <b>the rebel</b>, <b>the caregiver</b>, and <b>the creator</b> all share the occupation 
    <b>stage actor</b> as the most frequent in their respective distributions, appearing between 600 and 1,400 times 
    in the actor's occupations for each persona. This suggests that experience in stage acting may significantly 
    contribute to an actor's ability to perform major personas in films.<br><br>
    Occupations such as <b>screenwriter</b>, <b>film producer</b> and <b>film director</b> are also highly present, 
    appearing 450 to 900 times for each persona and frequently ranking in the Top-5 occupations. Although not directly 
    related to acting, these roles may help actors gain a deeper understanding of film production processes. For 
    instance, screenwriting experience may enhance an actor’s ability to interpret and deliver a script effectively.<br><br>
    The persona <b>the orphan</b> is closely linked to the occupations <b>voice actor</b> (around 400 times) and 
    <b>singer</b> and <b>model</b> (each appearing approximately 380 times). This indicates that portraying this persona 
    often requires skills in vocal and physical expression, essential for conveying vulnerability and emotional depth.<br><br>
    For the persona <b>the magician</b>, the occupation <b>voice actor</b> is particularly prominent, suggesting that 
    this role demands strong vocal interpretation. This can be explained by the fact that the <b>magician</b> persona 
    often exists in fantasy world, requiring a fantastical and immersive vocal performance to enhance the audience's experience.<br><br>
    In the personas <b>the seducer</b> and <b>the lover</b>, the occupations <b>model</b> and <b>voice actor</b> frequently 
    appear in the Top-5 occupations, with counts of approximately 400 and 650 times, respectively. This reinforces the 
    idea that these personas require a strong ability to express emotions through both vocal performance (as a 
    <b>voice actor</b>) and physical presence (as a <b>model</b>). Additionally, <b>the lover</b> persona often involves 
    the occupation <b>singer</b> (appearing around 600 times), which aligns with its frequent representation in musical 
    comedies, requiring singing abilities.<br><br>
    For the persona <b>the rebel</b>, the occupations <b>voice actor</b> (around 950 times) and <b>singer</b> (around 
    600 times) are also prominent. This suggests that this persona often necessitates strong vocal skills to convey 
    various emotional nuances effectively.<br><br>
    For the persona <b>the mentor</b>, the occupation <b>stage actor</b> is the most present, appearing approximately 
    750 times, but <b>voice actor</b> is in second place, with around 520 occurrences. This suggests that this persona 
    demands strong acting skills, also very present in theater, where depth and intensity of expression are crucial.<br><br>
    The <b>caregiver</b> persona is particularly intriguing due to the wide variety of occupations associated with it, 
    each with a significant count. <b>Stage actor</b> appears most frequently (around 1,400 times), followed by 
    <b>voice actor</b> (approximately 1,000 times). Additionally, <b>singer</b> and <b>model</b> are also very present, 
    with counts of about 650 and 700 times. This indicates that the <b>caregiver</b> persona is multifaceted and requires 
    a diverse range of skills, including vocal skills expressions, physical expression, and emotional depth.<br><br>
    Similar to <b>the rebel</b>, the persona <b>the creator</b> is strongly linked to <b>stage actor</b> (about 550 times) 
    and <b>voice actor</b>, reinforcing the need for robust acting abilities to perform this role effectively.<br><br>
    The persona <b>the joker</b> is also closely associated with <b>stage actor</b> (around 500 times) and <b>voice actor</b> 
    (approximately 550 times). This reflects the role's demand for strong acting performances, with a particular focus 
    on vocal delivery to convey its humorous and expressive aspects.<br><br>
    Lastly, the persona <b>the child</b> is predominantly connected to <b>voice actor</b>, which is explained by the 
    fact that many child characters are acted by adults. This reliance on voice acting highlights the need for vocal 
    adaptability to convincingly represent young characters.<br><br>
</p>

# What are the possible career paths, steps and possible trajectories ?
<iframe src="src/graphs//actor_movies_rating_graph.html" width="1200" height="800"></iframe>
<iframe src="src/graphs/movies_budget_revenue_ratings_graph.html" width="1200" height="800"></iframe>

# Does the academic and environmental background of an actor have an impact on his career success ?

## Family environment

### Parents relations
<p style="flex: 1; text-align: justify">
    It is interesting to study whether having one or two parents in the cinematographic world could have a positive impact 
    on the success of an actor's career. You can see below a bar chart that presents the number of actors who have at least 
    one parent who is also an actor.
</p>

<iframe src="src/graphs/actors_parents_number_distribtion.html" width="1200" height="800"></iframe>

<p style="flex: 1; text-align: justify">
    In addition to the graph, the majority of actors (48,438) defined in our analysis do not have at least one parent in 
    the cinematographic field and therefore did not have parental influence in the acting industry. At the same time, we 
    can see from the graph that 982 actors have one actor parent, and 193 have both parents in the acting field. This is 
    very interesting, and we will now examine whether the popularity of actor parents could have a correlation with the 
    actor's popularity. Finally, there is one actor with three parents in the acting field, which could be the case in 
    a recomposed family.<br><br>
    You can see below an interactive scatter plot that present the relationship between an actor's popularity and one of their parent's 
    popularity. You can select the type of popularity score used to compare the two popularities: the <b>opinion score</b> 
    (extracted from Part 1), the <b>award score</b> (extracted from Part 2), and the <b>overall score</b> (a combination 
    of the opinion score and award score) using the picker in the top-right corner of the graph.
</p>

<iframe src="src/graphs/actors_parents_popularity_correlation.html" width="1200" height="800"></iframe>

<p style="flex: 1; text-align: justify">
    In complement of the graph, the correlation for the popularity score obtained from the <b>public's opinion</b> 
    (extracted from Part 1) between the actor and their parent is 0.113. This means that the actor's popularity is very 
    slightly influenced by their parent’s <b>opinion score</b> popularity, as the covariance is very close to 0 this 
    influence is very not important. We observe the same pattern for the <b>award popularity score</b>(correlation : 0.074) and the 
    <b>overall score</b> (correlation: 0.080). Even though the influence is slightly smaller in these cases, since the correlation score is 
    more small. This is particularly evident for the overall score, as it is calculated using a combination of 
    the opinion and award scores. Therefore, while there is a small positive relationship along all the popularity score, 
    it is not significant enough to conclude that the actor's popularity is heavily dependent on the popularity of their 
    parents.<br><br>
    Now, we can see on the graph that some actors, such as Angelina Jolie, who have a very famous parent Jon Voight, are 
    also very famous themselves. These actors appear in the top-right corner of the graph, where both the actor's and parent's 
    popularity scores are high.<br><br>
    However, there are also actors with famous parents who are not as famous themselves and they are positioned along 
    the y-axis. This suggests that despite having a well-known parent, their own popularity does not achieve the popularity 
    of their parent.<br><br>
    In opposition, there are famous actors who do not have famous parents. While this could indicate that the actor's success 
    is largely independent of their parent. We could also argue that the parent's influence could still play a role due 
    to their experience and knowledge of the cinematic field. Even if this influence is not evident in terms of popularity 
    scores, it might still have an impact on the actor's career. These actors are present along the x-axis and there is a 
    lot of actors in this case.<br><br>
</p>