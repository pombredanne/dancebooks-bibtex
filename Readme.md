# dancebooks-bibtex

Данный проект ставит целью собрание наиболее полной библиографии по историческим танцам. База данных хранится в формате `.bib` и предполагает интеграцию с пакетами обработки языка разметки LaTeX.

Обработка библиографической базы данных в LaTex выполняется двумя программами: фронтэндом (на стороне LaTeX) и бэкэндом (именно бэкэнд считывает базу данных и преобразует её в формат, понятный LaTeX'у). Теоретически, можно использовать любую существующую связку (фронтэнд + бэкэнд), официально поддерживаются две: `(natbib + bibtex8)` и `(biblatex + biber)`. Про них будет рассказано ниже. Кроме базы данных, реализованы собственные стилевые файлы для официально поддерживаемых связок (фронтэнд + бэкэнд).

Кроме этого в проект включены некоторые транскрипции танцевальных источников в формате [markdown](http://daringfireball.net/projects/markdown/syntax). Некоторые правила оформления данных источников описаны ниже.

## (natbib + bibtex8-bit):

Требует наличия пакетов `natbib` и `bibtex8-bit` (есть в стандартном репозитории). Подключение библиографии производится следующей командой:

	\newcommand{\rootfolder}{%folderpath%}
	\usepackage[root=\rootfolder]{\rootfolder/dancebooks-bibtex}

Здесь `%folderpath%` - путь к папке с библиографией (обратные слеши нужно заменить на прямые для корректной работы). В этой путь не должно быть последнего слэша.

Неправильно:

	D:\georg\dancebooks-bibtex
	D:/georg/dancebooks-bibtex/

Правильно:

	D:/georg/dancebooks-bibtex

После подключения пакета становятся доступны макросы цитирования `\cite{id}`, `\footcite{id}`, `\parencite{id}`, `\nocite{id}` и макрос печати библиографии `\printbibliography` с одним опциональным параметром, позволяющим перечислить дополнительный библиографические источники (.bib-файлы) через запятую без указания расширения (расширение `.bib` будет подставлено автоматически).
Пример использования:

	\printbibliography{hello,extra,file}

## (biblatex + biber):

С использованием этих пакетов дело обстоит несколько сложнее. Нужно установить `biblatex`, `biblatex-gost` и `biber` (про установку данных пакетов можно будет прочесть ниже. Стилевой файл подключается аналогично:

	\newcommand{\rootfolder}{%folderpath%}
	\usepackage[root=\rootfolder]{\rootfolder/dancebooks-biblatex}
	
Опционально доступен параметр `detailed`, принимающий значения `true` и `false`. При указании значения `true` включается печать служебной информации (наличие транскрипций, уточнение датировки и так далее). Значение по умолчанию – `false`. Пример использования опции:

	\newcommand{\rootfolder}{%folderpath%}
	\usepackage[detailed=true,root=\rootfolder]{\rootfolder/dancebooks-biblatex}
	
Опционально доступен параметр `usedefaults`, принимающий значения `true` и `false. При указании значения `false` источники танцевальной библиографии (`.bib`-файлы из состава проекта) не подключаются. Позволяет использовать стилевой файл из дистрибутива в других проектах. Пример использования опции:

	\newcommand{\rootfolder}{%folderpath%}
	\usepackage[usedefaults=false,root=\rootfolder]{\rootfolder/dancebooks-biblatex}

После подключения становятся доступны макросы цитирования `\cite`, `\footcite`, `\parencite`, `\nocite`, `\volcite`. Работа макросов описана в [biblatex manual](http://mirrors.ctan.org/macros/latex/contrib/biblatex/doc/biblatex.pdf). Стандартный макрос печати библиографии в `biblatex` -- `\printbibliography`, без параметров. Дополнительные библиографические источники можно добавить стандартной командой `\addbibresource{hello.bib}` (расширение `.bib` необходимо указывать явно).

Порядок компиляции такой:

1. pdflatex project.tex
2. bibtex8 --wolfgang project
3. pdflatex project.tex
4. pdflatex project.tex

### Установка допольнительных пакетов. `biblatex`:

Скачать можно [по этому адресу](http://sourceforge.net/projects/biblatex/files/).

Пакет есть в стандартном репозитории.

### Установка допольнительных пакетов. `biber`:

Скачать бэкэнд можно [по этому адресу](http://sourceforge.net/projects/biblatex-biber/files/biblatex-biber/). Внимание! Не всякая версия biber подходит для конкретной версии biblatex. Изучите, пожалуйста, информацию о необходимой вам версии biber.

Необходимо положить исполняемый файл в любую папку, после чего добавить эту папку в `%PATH%`, если этого не было сделано раньше.

Для x86-дистрибутивов пакет есть в стандартном репозитории (для MiKTeX он называется `miktex-biber-bin`).

### Установка допольнительных пакетов. `biblatex-gost`:

Скачать последнюю версию гостовских стилей можно [по этому адресу](http://sourceforge.net/projects/biblatexgost/files/).

Скачанный архив нужно распаковать (с сохранением структуры директорий) в любую из корневых папок вашего дистрибутива.

После установки пакета нужно выполнить команду обновления кэша (команда зависит от вашего дистрибутива, для MiKTeX – `"initexmf -u"`).

Порядок компиляции такой:

1. pdflatex project.tex
2. biber project
3. pdflatex project.tex
4. pdflatex project.tex (в Makefile из библиографии этот пункт отсутсвует, поскольку в выходных файлах нет содержания)

## Правила оформления транскрипций в формате `markdown`:

Из текстов траскрипций удаляются номера страниц, поскольку транскрипция не является и не должна являться полноценной заменой бумажной книги или её факсимильной копии.

Файлы транскипций находятся в кодировке utf-8-without-bom.

Для просмотра файлов можно установить расширения веб-браузера: [Firefox Markdown Viewer](https://addons.mozilla.org/en-US/firefox/addon/markdown-viewer/) (стоит отметить, что для больших файлов расширение работает довольно медленно) или использовать скрипт `transcriptions/_markdown2.py` (потребуется `python` с установленным модулем `markdown2`).

### Правила расстановки заголовков таковы:

* \# – ставится у названия книги,
* \#\# – ставится у автора книги или авторов, если их несколько,
* \#\#\# – ставится у всех прочих заголовков других уровней.

После символов форматирования в разметке присутствует пробел.

### Правила, применяемые при оформлении транскрипций:
Вот короткий список изменений, которые я провожу с текстом транскрипции:

* Удаляются номера страниц и символы переноса внутри слов (это облегчает контекстный поиск),
* \<, &amp;lt; и \>, &amp;gt; заменяются на ‹ и › соответственно,
* — (длинное тире) заменяется на короткое (–),
* В словах (по возможности) ставится буква ё вместо е там, где это необходимо,
* Инициалы пишутся через пробел,
* Стихи и отрывки из произведений оформляются как цитаты (> ),
* Короткие (однострочные) сноски вносятся прямо в текст, остальные ограничиваются горизонтальными линиями сверху и снизу (\*\*\*),
* В конце заголовков удаляются точки,
* В конце строк обрезаются пробельные символы.

Возможны и некоторые другие специфичные для каждой транскрипции в отдельности изменения.