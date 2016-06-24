#Carola Frediani Feed RSS

###Perchè nasce questo progetto:

Il quotidiano La Stampa non permette di ricevere notifiche di nuove pubblicazioni o di effettuare ricerche su un singolo autore, limitando pertanto la possibilità di rimanere aggiornati sugli ottimi articoli scritti da Carola.

Nonostante la nostra amicizia su Facebook e Twitter a volte perdo per strada i suoi ottimi articoli, sono da sempre un fondato sostenitore dei Feed RSS pertanto ho pensato di realizzare questo semplice progetto Open Source. Per chi fosse interessato al codice lo trova su GitHub.

###Come funziona:

1. È presente un cron che ogni 30 minuti analizza il Feed RSS integrale della La Stampa;
2. Per ogni articolo pubblicato fa uno scrap del codice HTML alla ricerca del tag "article-author";
3. Se il tag corrisponde con "carola frediani" o "frediani carola" viene aggiornato il Feed RSS in XML;
4. Il Feed RSS dedicato a Carola conterrà, come da standard, l'ultimo articolo in cima. Vengono inoltre rimossi eventuali duplicati;
5. Il Feed conterrà il Titolo, Link, Data (approssimativa) e Contenuto dell'articolo;
6. Il contenuto viene reso "leggibile" con le dedicate librerire di Python (readability.com sulla La Stampa non funziona) e nel feed vengono riportati i soli primi 400 caratteri (HTML compreso, ovvero poco più di 100 caratteri di testo puro). Volutamente, per continuare la lettura si dovrà accedere al sito originale.

###Feed RSS:

Il Feed RSS è disponibile al seguente URL: http://carola.draghetti.it/carolafeed.xml

###License

GNU General Public License version 2.0 (GPLv2)

###Credits

* [Andrea Draghetti](https://twitter.com/AndreaDraghetti) is the creator of the project

Special thanks:

* [Padraic Cunningham](http://stackexchange.com/users/2456564/padraic-cunningham?tab=accounts) to support for coding.

### Requirements
- Python
- bs4 (pin install bs4)
- feedparser (pip install feedparser)
- readability-lxml (pip install readability-lxml)
