# Error analysis — xlmr-sentitriage

Test set: 870 tweets. Accepted: 678, abstained: 192.

## Confident errors (accepted and wrong)

| Text | Gold | Pred | Conf. | Action |
|---|---|---|---|---|
| @user @user @user @userMujer que trabajo tan sufrido se pasa mál verdad jajaja  eso es bueno muchos mimos | neutral | positive | 0.86 | PASS |
| @user definitivamente haberla fastidiado, es un tio super agradable y que transmite un buen rollo increible | neutral | positive | 0.86 | PASS |
| @user me ofrecería pero gerald es demasiado lindo | neutral | positive | 0.86 | PASS |
| @user Es que me gusta muchísimo... Pero me da un palo enorme pagar... Que ya lo hice (Y mucho) con WoW ... | neutral | positive | 0.86 | PASS |
| Limo sadboy de mierda la vida es maravillosa | neutral | positive | 0.86 | PASS |
| Se ha acabado el mes más bonito del año | negative | positive | 0.86 | PASS |
| @user tan linda Diana, muchas gracias vamos a ver cómo me acomodo ahora con trabajo nuevo, cuesta un montón yo te apoyo desde acá! | neutral | positive | 0.86 | PASS |
| @user @user lo dice para hacernos sentir mejor u.u jaja...Pero bueno eres más joven tienes mucho por ver y hacer . Éxitos! | neutral | positive | 0.86 | PASS |


## Complaints passed silently (gold negative, action PASS)

| Text | Gold | Pred | Conf. | Action |
|---|---|---|---|---|
| Se ha acabado el mes más bonito del año | negative | positive | 0.86 | PASS |
| Las personas jóvenes no deberian partir . Un muchacho super emprendedor y lleno de sueños se fue Mucha fuerza a la familia y amigos. | negative | positive | 0.85 | PASS |
| @user que tiene de gracioso | negative | positive | 0.85 | PASS |
| Uno de los peores dias | negative | positive | 0.84 | PASS |
| Es gracioso cuando intentan sacarte del medio aprovechándose de los sentimientos de otros y poniendo buena cara... Nadie se lo espera | negative | positive | 0.84 | PASS |
| Que madre con el @user, increíble como unos platudos de Singapur, Jorge Mendes y el otro representante se pasearon en mi Valencia | negative | positive | 0.84 | PASS |
| q los GP de La Caixa (y otros) manipulen el Ibex es una bendició gracias a ellos podemos arrañar alg son auténticos PARDILLOS | negative | positive | 0.84 | PASS |
| @user perfecto. ¡Gracias! A ver cuánto me toca pagar este año, que ya 3 años he pagado lo mismo. | negative | positive | 0.84 | PASS |


## Errors caught by abstention (wrong, but the agent abstained)

| Text | Gold | Pred | Conf. | Action |
|---|---|---|---|---|
| Pero qué rico es dormir hasta las 9'41 am , te sientes tan vago | neutral | positive | 0.36 | ABSTAIN |
| @user JA JA JA JA JA  Teneis el ojino como la bandera de Japón ,hijos de la gran puta | negative | positive | 0.46 | ABSTAIN |
| @user pero eso no es grasioso | negative | neutral | 0.47 | ABSTAIN |
| @user es que la intimidas | negative | neutral | 0.47 | ABSTAIN |
| Típico: Te levantas de noche para ir al baño y corres lo más veloz que puedes para que el fantasma no te alcance | neutral | negative | 0.47 | ABSTAIN |
| Cambiar "El mejor sistema™" y la educación médica en España será complicado, pero con gente como vosotros tengo fe  @user @user | positive | neutral | 0.47 | ABSTAIN |
| @user , no hay que sentirse mal por ya no querer creo que es bueno saber lo que uno quiere y lo que no | positive | neutral | 0.47 | ABSTAIN |
| @user Guitar ya sabes que hacer. El otro día estuve en llamada contigo por Green.  A ver si unas públicas, aún que sea malo... | neutral | negative | 0.48 | ABSTAIN |


## Confident correct decisions

| Text | Gold | Pred | Conf. | Action |
|---|---|---|---|---|
| @user pero igual es feo, horrible, espantoso | negative | negative | 0.88 | QUEUE |
| Y eso es triste la vdd. Por vosotros, no por mi | negative | negative | 0.88 | QUEUE |
| @user No para esa hora. Es devastador el efecto de #OttoCR en mi país en realidad | negative | negative | 0.88 | QUEUE |
| @user ...nada queda de ese Canal N que informaba la verdad cuando todos los medios estaban vendidos, que pena | negative | negative | 0.87 | QUEUE |
| @user buen duo con Manolo B. En cuatro linda cancion. . como tantas de mar de copas q estan en el soundtrack de mi vida. | positive | positive | 0.87 | PASS |
| Lo peor es que esos materiales no están regularizados por su culpa. Y la computadora es lenta porque no nos la quiere cambiar | negative | negative | 0.87 | QUEUE |
| @user Buenooo, claro que si y a @user se le está pegando...Pero es estupendo. Scoop. No dejéis de verla. | positive | positive | 0.87 | PASS |
| Mi usb de mierda está malogrado y se me borró TODA MI PUTA INFO de eeggll ensayo de argu, monografia de investiga, los extrañaré | negative | negative | 0.87 | QUEUE |


## Confusion between classes (all test, without abstention)

| gold     |   negative |   neutral |   positive |
|:---------|-----------:|----------:|-----------:|
| negative |        213 |        49 |         28 |
| neutral  |         80 |       137 |         73 |
| positive |         24 |        35 |        231 |
