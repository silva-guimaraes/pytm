pega informações sobre a duração de cada faixa [nesse site](https://rateyourmusic.com/) e usa isso pra cortar o video baixado do youtube em varias partes. é bem gambiarra.


### exemplo
```sh
pytm 'https://www.youtube.com/watch?v=TPYqrVDlc_4' 'https://rateyourmusic.com/release/album/various-artists/mikgazer-vol_1/'
```
é possivel também que o video possua capítulos, nesse caso, o script entende que o corte pode ser feito através desses capítulos se nenhum link para o rateyourmusic for especificado
```sh
pytm 'https://www.youtube.com/watch?v=TPYqrVDlc_4'
```
