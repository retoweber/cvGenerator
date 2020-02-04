# CV Generator

This is a program generating a CV as a pdf and a html.

## Getting Started

```
git clone https://github.com/retoweber/cvgenerator
```

### Prerequisites
You need `texlive-xetex` and `python3` (the latter should be already installed on most linux distributions.)
```
sudo apt-get install texlive-xetex
```
For handeling json you need `jq`
```
sudo apt-get install jq
```
You also need the python libraries `json`, `os`, `re` which should be shipped with the standard `python3`.

### Usage
There is only one command to execute.
```
python3 generate.py
```
## Adapt templates
There is a html template `htmlTemplate.html` and a latex template `latexTemplate.tex`. You can alter these to change the design.
### Overview
I defined placeholders in the templates. These look something like
```
<!-- !TEMPLATE ["personalInformation"]["firstName"] -->
```
in html or for latex
```
\template{["personalInformation"]["firstName"]}
```
As one can maybe guess there needs to be a file from where this data is filled in. This file is called `cv.json`. The cv generator opens this file and accesses, for the above examples, the field `["personalInformation"]["firstName"]`. So you are free to extend the `cv.json` however you want.

In addition to this the program is also able to execute loops. Here are two examples. One in html and one in latex.
```
<!-- !TEMPLATE LOOP "i" ["experience"]["list"] -->
    <p>hello world</p>
    <!-- !TEMPLATE ["experience"]["list"][i] -->,
<!-- !TEMPLATE ENDLOOP "i" -->
```
```
\template{LOOP "i" ["experience"]["list"]}
    \par{hello world}
    \template{["experience"]["list"][i]},
\template{ENDLOOP "i"}
```

* You have to define the control variable (here `"i"`) in the beginning of the loop and the end of the loop (`LOOP "i"`, `ENDLOOP "i"`).
* The accessed field in the Loop (in the above example `["experience"]["list"]`) has to point to a list in the `cv.json`.
* The generator then adds everything in the loop body as many times as the referenced list is long.
* In the loop body you can access the single elements of the list with the control variable (here `i`).
* The above examples will write for every entry in the `["experience"]["list"]`-list: `hello world ` and adds the entry of the list at the end.
* You can also have nested loops but then the control variable have to be different.

Please take a look at the templates. They are not difficult to understand.

Because I defined this template markup language the generator is by no means bound to this template or even to html and latex. Feel free to change anything you want.

## Bugs
There is no known bug. But if some output is not as you expected please consider reading the functions `sanatizeHtml()` and `sanatizeLatex()` in `generate.py`. It capitalizes things automatically and removes commas if they are at the end of a line and much more.

## Autor
**Reto Weber** - (https://github.com/retoweber, http://retoweber.info)

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
