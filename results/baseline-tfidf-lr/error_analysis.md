# Error analysis — baseline-tfidf-lr

Test set: 870 tweets. Accepted: 330, abstained: 540.

## Confident errors (accepted and wrong)

| Text | Gold | Pred | Conf. | Action |
|---|---|---|---|---|
| La escena spoby es tan bonita y tan triste y no paro de llorar damn | neutral | negative | 0.92 | QUEUE |
| @user que tiene de gracioso | negative | positive | 0.89 | PASS |
| @user que tengas un lindo jueves ... | neutral | positive | 0.84 | PASS |
| @user @user lo dice para hacernos sentir mejor u.u jaja...Pero bueno eres más joven tienes mucho por ver y hacer . Éxitos! | neutral | positive | 0.84 | PASS |
| @user que es muy cara | negative | positive | 0.83 | PASS |
| No es que me volví "ANTISOCIAL", eso nunca, solo que por respeto a mis criterios y lógicas me volví un "ANTIALGUNASPERSONAS" nada mas | neutral | negative | 0.83 | QUEUE |
| Debo dejar de hacer bromas porque cuando hable en serio no me creerán | neutral | negative | 0.82 | QUEUE |
| Bueno que buenas noches tras el bajón de las 03:24 | negative | positive | 0.81 | PASS |


## Complaints passed silently (gold negative, action PASS)

| Text | Gold | Pred | Conf. | Action |
|---|---|---|---|---|
| @user que tiene de gracioso | negative | positive | 0.89 | PASS |
| @user que es muy cara | negative | positive | 0.83 | PASS |
| Bueno que buenas noches tras el bajón de las 03:24 | negative | positive | 0.81 | PASS |
| @user Espero que te mejores pronto, vomitar es muy desagradable | negative | positive | 0.80 | PASS |
| Se ha acabado el mes más bonito del año | negative | positive | 0.77 | PASS |
| Yo quería que Callie y Wyatt siguiesen juntos | negative | neutral | 0.67 | PASS |
| @user eres un carca tio | negative | positive | 0.65 | PASS |
| @user faltabas mi samo, la familia unida jajajajaja, te extraño, venn | negative | neutral | 0.65 | PASS |


## Errors caught by abstention (wrong, but the agent abstained)

| Text | Gold | Pred | Conf. | Action |
|---|---|---|---|---|
| @user por que tan bajito? | neutral | negative | 0.35 | ABSTAIN |
| Cuando uno siente que se complementa y pasa momentos increíbles con una persona se da cuenta que no es necesario contar con muchos | positive | neutral | 0.35 | ABSTAIN |
| Tarzan en disney channel, por si queréis escapar de la morralla típica de un sábado por la tarde | neutral | negative | 0.35 | ABSTAIN |
| @user TE AMOOOOOO CSM A LA FI,y la verdad que eres la única que soporto de las amigas de tú sabes quien jeje | positive | negative | 0.36 | ABSTAIN |
| @user me fascinas , me provocas , me arrechas !!!! Quiero conocerte y cogerte como nunca e cogido a nadie | positive | negative | 0.36 | ABSTAIN |
| @user necesitamos fuentes con pitorro en Vallecas, que la mayoría están rotas  @user | negative | positive | 0.36 | ABSTAIN |
| Cambiar "El mejor sistema™" y la educación médica en España será complicado, pero con gente como vosotros tengo fe  @user @user | positive | neutral | 0.37 | ABSTAIN |
| @user @user si haase hace otro set y janowicz el over. Me voy a estar acordando del puto chino toda noche...... | negative | positive | 0.37 | ABSTAIN |


## Confident correct decisions

| Text | Gold | Pred | Conf. | Action |
|---|---|---|---|---|
| @user buen tip muchas gracias | positive | positive | 0.98 | PASS |
| @user muchas gracias, Francisco!! feliz día | positive | positive | 0.98 | PASS |
| @user mil gracias, Ana! feliz noche, guapa | positive | positive | 0.97 | PASS |
| @user muchísimas gracias!!! Un fuerte abrazo | positive | positive | 0.97 | PASS |
| @user gracias por tu "Me Gusta" guapa!! Eres una gran actriz y me encantas desde la serie El Grupo, q estuviste genial | positive | positive | 0.96 | PASS |
| @user @user @user ¡Gracias por acompañarnos! Fue una gran noche | positive | positive | 0.96 | PASS |
| @user gracias, preciosa!! #FF para ti por tu aportación y generosidad | positive | positive | 0.96 | PASS |
| Me encanta estar así de feliz...ojalá y esto toda la vida!!! Buenisimas noches  Gracias, te amo @user 😙😘 | positive | positive | 0.95 | PASS |


## Confusion between classes (all test, without abstention)

| gold     |   negative |   neutral |   positive |
|:---------|-----------:|----------:|-----------:|
| negative |        181 |        62 |         47 |
| neutral  |         89 |       116 |         85 |
| positive |         53 |        61 |        176 |
