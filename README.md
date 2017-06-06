# RSS Feed Generator

### Perchè nasce questo progetto:

Il progetto nasce con l'itento di creare un Feed RSS di ogni articolo scritto da Carola Frediani, poichè il quotidiano La Stampa non permette di ricevere notifiche di nuove pubblicazioni o di effettuare ricerche su un singolo autore, limitando pertanto la possibilità di rimanere aggiornati sugli ottimi articoli scritti da Carola.

Successivamente il progetto si è amplicato creando generatori di Feed RSS anche per altri fonti che non prevedono automaticamente la geneazione di un Feed.

## Funzionamento Feed Carola Frediani

1. È presente un cron che ogni 30 minuti analizza il Feed RSS e Homepage della La Stampa;
2. Per ogni articolo pubblicato fa uno scrap del codice HTML alla ricerca del tag "article-author";
3. Se il tag corrisponde con "carola frediani" o "frediani carola" viene aggiornato il Feed RSS in XML;
4. Il Feed RSS dedicato a Carola conterrà, come da standard, l'ultimo articolo in cima. Vengono inoltre rimossi eventuali duplicati;
5. Il Feed conterrà il Titolo, Link, Data (approssimativa) e Contenuto dell'articolo;
6. Il contenuto viene reso "leggibile" con la libreria Readability e nel feed vengono riportati i soli primi 400 caratteri (HTML compreso, ovvero poco più di 100 caratteri di testo puro). Volutamente, per continuare la lettura si dovrà accedere al sito originale.

### Feed RSS:

I Feed RSS generati sono disponibi su: https://rss.draghetti.it/

### License

GNU General Public License version 2.0 (GPLv2)

### Credits

* [Andrea Draghetti](https://twitter.com/AndreaDraghetti) is the creator of the project

Special thanks:

* [Padraic Cunningham](http://stackexchange.com/users/2456564/padraic-cunningham?tab=accounts) to support for coding.

### Requirements
- Python
- bs4 (pip install bs4)
- feedparser (pip install feedparser)