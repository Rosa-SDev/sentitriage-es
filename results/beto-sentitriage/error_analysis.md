# Error analysis — beto-sentitriage

Test set: 870 tweets. Accepted: 657, abstained: 213.

## Confident errors (accepted and wrong)

| Text | Gold | Pred | Conf. | Action |
|---|---|---|---|---|
| Tengo 4 horas de "webin" y ni idea de qué hacer  Aquí no puedo poner música a lo fiesta patronal como con Sarita o Max | neutral | negative | 0.88 | QUEUE |
| @user menuda forma más gratuita de dar envidia por twitter | negative | positive | 0.88 | PASS |
| @user thanks weapon bonico,♡ sí, ya estoy en el aeropuerto y fíjate tú ni me da pena. Anoche el calor fue HORROROSO no he dormido ná. | neutral | negative | 0.88 | QUEUE |
| @user tan linda Diana, muchas gracias vamos a ver cómo me acomodo ahora con trabajo nuevo, cuesta un montón yo te apoyo desde acá! | neutral | positive | 0.87 | PASS |
| @user @user pobre @user ...le habrá dejado la mano roja de agarrarle tan fuerte | neutral | negative | 0.87 | QUEUE |
| @user sin ellas todo sería muy aburrido | positive | negative | 0.87 | QUEUE |
| Estoy tan cansada que no veré ninguna serie cuando llegue a casa | neutral | negative | 0.87 | QUEUE |
| cada vez que cito un tweet se va la ubicación sin tampoco poder ponerla en el momento a uds les pasa? TE VEO Y ME PICA VICICONTE | neutral | negative | 0.87 | QUEUE |


## Complaints passed silently (gold negative, action PASS)

| Text | Gold | Pred | Conf. | Action |
|---|---|---|---|---|
| @user menuda forma más gratuita de dar envidia por twitter | negative | positive | 0.88 | PASS |
| Se ha acabado el mes más bonito del año | negative | positive | 0.86 | PASS |
| @user perfecto. ¡Gracias! A ver cuánto me toca pagar este año, que ya 3 años he pagado lo mismo. | negative | positive | 0.86 | PASS |
| Que madre con el @user, increíble como unos platudos de Singapur, Jorge Mendes y el otro representante se pasearon en mi Valencia | negative | positive | 0.84 | PASS |
| Todo el mundo con la segunda temporada de Narcos y yo no, PORQUE NO TENGO NETFLIX @user pasaros una suscripcion de 5 dias | negative | neutral | 0.83 | PASS |
| @user @user Metáfora=Comparación, que es lo que dije. Un poquito de teoría literaria | negative | neutral | 0.83 | PASS |
| @user el rottweiler es precioso pero... Esta zumbadisimo y ataca  y yo muero de ganas de achucharlo | negative | positive | 0.82 | PASS |
| q los GP de La Caixa (y otros) manipulen el Ibex es una bendició gracias a ellos podemos arrañar alg son auténticos PARDILLOS | negative | positive | 0.80 | PASS |


## Errors caught by abstention (wrong, but the agent abstained)

| Text | Gold | Pred | Conf. | Action |
|---|---|---|---|---|
| @user me ofrecería pero gerald es demasiado lindo | neutral | positive | 0.35 | ABSTAIN |
| Nosotras somos muy interesantes, sí. Y no tenemos abuela @user   ¡Os echamos de menos la otra semana! | positive | negative | 0.40 | ABSTAIN |
| @user regleta o gusanillo… creo que quedara mejor lo segundo | neutral | positive | 0.41 | ABSTAIN |
| Buenos días. Lunes duro de vuelta al trabajo, al calor, al metro, a los madrugones y a la rutina  #BuenosDias | negative | positive | 0.41 | ABSTAIN |
| Pero qué rico es dormir hasta las 9'41 am , te sientes tan vago | neutral | positive | 0.41 | ABSTAIN |
| Cuando ves a alguien que te lo ha hecho pasar tan mal, pero no sientes nada. Eso es lo mejor que te puede pasar | positive | neutral | 0.43 | ABSTAIN |
| Ya me dio nostalgia viendo tantos videos de clásicos antiguos | positive | negative | 0.43 | ABSTAIN |
| @user @user Un capullo menos en el Valencia. Si no esta al 100% con el Valencia lo mejor es venderlo. | negative | neutral | 0.43 | ABSTAIN |


## Confident correct decisions

| Text | Gold | Pred | Conf. | Action |
|---|---|---|---|---|
| @user Qué guay tus padres, los míos igual! Si te gusta, lánzate, que es muy bonita | positive | positive | 0.90 | PASS |
| @user es que me da pena porque creo que tengo cuatro pares diferentes de 20 y están ahí cogiendo polvo las pobres | negative | negative | 0.89 | QUEUE |
| @user Que rico! Provecho en su día | positive | positive | 0.89 | PASS |
| no me deis confianza que luego os digo las cosas muy claras y os jode | negative | negative | 0.89 | QUEUE |
| @user genial! Ahora ya mucho mejor que con las tres primeras aún así todavía hay cosas que pulir | positive | positive | 0.89 | PASS |
| @user @user qué juegazo! Bueno, súper bonito y barato | positive | positive | 0.89 | PASS |
| estar en tumblr/ we heart it, el internet en general es tan frustrante porque veo arte tan hermoso y siento q lo que yo hago es tan | negative | negative | 0.88 | QUEUE |
| @user Pues muchas gracias, nuestras puertas están siempre abiertas, que bueno que hays disfrutado de la ponencia. | positive | positive | 0.88 | PASS |


## Confusion between classes (all test, without abstention)

| gold     |   negative |   neutral |   positive |
|:---------|-----------:|----------:|-----------:|
| negative |        205 |        65 |         20 |
| neutral  |         64 |       180 |         46 |
| positive |         16 |        62 |        212 |
