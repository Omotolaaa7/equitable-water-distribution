%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% ama-article.cls
%% Classe LaTeX pour les articles scientifiques de l'AMA
%% (Academie des Mathematiques Appliquees)
%%
%% Maquette calquee sur la classe elsarticle (Elsevier) :
%%   bandeau de revue (logo + sommaire en ligne) -> titre -> auteurs et
%%   affiliations -> bloc "Informations / Resume" en vis-a-vis -> corps
%%   -> references -> annexes, avec en-tetes courantes et notes de
%%   premiere page (correspondance, adresses electroniques, ISSN, DOI).
%% Version 2.0
%%
%% Utilisation : \documentclass[10pt]{ama-article}
%% Options     : 10pt | 11pt | 12pt   taille de police (defaut 10pt)
%%               french | english     langue principale (defaut french)
%%               twocolumn            corps sur deux colonnes
%%               anonyme              masque les auteurs (evaluation aveugle)
%%               brouillon            filigrane BROUILLON
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ama-article}[2026/09/03 v2.0 Article scientifique AMA]

%------------------------------------------------------------------------------
% 1. OPTIONS DE CLASSE
%------------------------------------------------------------------------------
\newif\ifama@english   \ama@englishfalse
\newif\ifama@anonyme   \ama@anonymefalse
\newif\ifama@brouillon \ama@brouillonfalse

\DeclareOption{french}    {\ama@englishfalse}
\DeclareOption{english}   {\ama@englishtrue}
\DeclareOption{anonyme}   {\ama@anonymetrue}
\DeclareOption{brouillon} {\ama@brouillontrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ExecuteOptions{10pt}
\ProcessOptions\relax
\LoadClass[a4paper]{article}

%------------------------------------------------------------------------------
% 2. ENCODAGE, POLICES, LANGUE
%------------------------------------------------------------------------------
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
\RequirePackage{lmodern}
\RequirePackage{textcomp}
\RequirePackage{microtype}

\ifama@english
  \RequirePackage[french,main=english]{babel}
\else
  \RequirePackage[english,main=french]{babel}
\fi
\RequirePackage{csquotes}

%------------------------------------------------------------------------------
% 3. GEOMETRIE DE LA PAGE (proche des revues Elsevier)
%------------------------------------------------------------------------------
\RequirePackage[a4paper,top=2.2cm,bottom=2.4cm,left=2.2cm,right=2.2cm,
                headheight=14pt,headsep=14pt,footskip=1.2cm]{geometry}
\RequirePackage{setspace}
\setlength{\parindent}{1.2em}
\setlength{\parskip}{0pt}

%------------------------------------------------------------------------------
% 4. MATHEMATIQUES
%------------------------------------------------------------------------------
\RequirePackage{amsmath,amssymb,amsfonts,amsthm}
\RequirePackage{mathtools}
\RequirePackage{bm}
\RequirePackage{siunitx}
\sisetup{per-mode=symbol,output-decimal-marker={,}}
\allowdisplaybreaks[1]

%------------------------------------------------------------------------------
% 5. FLOTTANTS, TABLEAUX, FIGURES
%------------------------------------------------------------------------------
\RequirePackage{graphicx}
\graphicspath{{figures/}{Figures/}{img/}}
\RequirePackage{xcolor}
\RequirePackage{booktabs}
\RequirePackage{array}
\RequirePackage{multirow}
\RequirePackage{longtable}
\RequirePackage{float}
\RequirePackage{subcaption}
\RequirePackage{pgfplots}
\pgfplotsset{compat=1.18}

% Legendes facon Elsevier : "Fig. 1." et "Table 1" en gras, texte petit
\RequirePackage[font=small,labelfont=bf,labelsep=period,
                justification=justified,singlelinecheck=false]{caption}
\ifama@english\else
  \addto\captionsfrench{%
    \renewcommand{\figurename}{Fig.}%
    \renewcommand{\tablename}{Tableau}%
  }
\fi

%------------------------------------------------------------------------------
% 6. LISTES, CODE, ALGORITHMES, ENCADRES
%------------------------------------------------------------------------------
\RequirePackage{enumitem}
\setlist[itemize]{label=\textbullet,itemsep=1pt,topsep=3pt,leftmargin=1.5em}
\setlist[enumerate]{itemsep=1pt,topsep=3pt,leftmargin=1.8em}

\RequirePackage{listings}
\RequirePackage{algorithm}
\RequirePackage{algpseudocode}
\RequirePackage[most]{tcolorbox}

%------------------------------------------------------------------------------
% 7. PALETTE : DOCUMENT MONOCHROME
%    Seule couleur : le bleu du logo, reserve aux hyperliens ecran.
%------------------------------------------------------------------------------
\definecolor{AMAlien}{HTML}{04325F}
\definecolor{AMAgris}{gray}{0.35}
\definecolor{AMAband}{gray}{0.94}   % fond du bandeau de revue
\definecolor{AMAfond}{gray}{0.96}

%------------------------------------------------------------------------------
% 8. HYPERLIENS ET RENVOIS
%------------------------------------------------------------------------------
\RequirePackage[colorlinks=true,linkcolor=AMAlien,citecolor=AMAlien,
                urlcolor=AMAlien,breaklinks=true]{hyperref}
\RequirePackage{url}
\RequirePackage{cleveref}

% babel-french rend ; : ! ? actifs. Ces caracteres actifs cassent les labels
% du type "sec:intro" dans cleveref, que babel ne patche pas comme \ref. Les
% commandes de cleveref etant robustes (\cref vaut "\protect\cref\space"), on
% remplace la commande interne, sous peine de recursion infinie.
\newcommand{\ama@safecref}[1]{%
  \expandafter\let\csname ama@orig@#1\expandafter\endcsname
                  \csname #1\space\endcsname
  \expandafter\def\csname #1\space\endcsname##1{%
    {\@safe@activestrue\csname ama@orig@#1\endcsname{##1}}}%
}
\newcommand{\ama@safecrefii}[1]{%
  \expandafter\let\csname ama@orig@#1\expandafter\endcsname
                  \csname #1\space\endcsname
  \expandafter\def\csname #1\space\endcsname##1##2{%
    {\@safe@activestrue\csname ama@orig@#1\endcsname{##1}{##2}}}%
}
\AtBeginDocument{%
  \@ifundefined{@safe@activestrue}{}{%
    \ama@safecref{cref}\ama@safecref{Cref}%
    \ama@safecref{cpageref}\ama@safecref{Cpageref}%
    \ama@safecrefii{crefrange}\ama@safecrefii{Crefrange}%
  }%
}

%------------------------------------------------------------------------------
% 9. BIBLIOGRAPHIE (natbib, appels numeriques : [1], [2,3], [4-6])
%------------------------------------------------------------------------------
\RequirePackage[numbers,sort&compress,square,comma]{natbib}
\setlength{\bibsep}{0pt plus 0.3pt}
\renewcommand{\bibfont}{\footnotesize}

%------------------------------------------------------------------------------
% 10. IDENTITE DE LA REVUE (bandeau de premiere page et en-tetes)
%------------------------------------------------------------------------------
\def\@ama@revue{Revue des Projets Scientifiques de l'AMA}
\newcommand{\revue}[1]{\def\@ama@revue{#1}}
\def\@ama@revuecourt{}
\newcommand{\revuecourt}[1]{\def\@ama@revuecourt{#1}}
\def\@ama@portail{le portail scientifique de l'AMA}
\newcommand{\portail}[1]{\def\@ama@portail{#1}}
% Accroche affichee dans le bandeau, au-dessus de l'adresse du site
\def\@ama@accroche{}
\newcommand{\accroche}[1]{\def\@ama@accroche{#1}}
\def\@ama@site{academiedesmathsappliquees.com}
\newcommand{\siterevue}[1]{\def\@ama@site{#1}}
% Adresse cliquable ; par defaut http:// suivi du site affiche
\def\@ama@url{}
\newcommand{\urlrevue}[1]{\def\@ama@url{#1}}
\newcommand{\ama@lien}{\ifx\@ama@url\@empty http://\@ama@site\else\@ama@url\fi}
\def\@ama@volume{}   \newcommand{\volume}[1]{\def\@ama@volume{#1}}
\def\@ama@annee{}    \newcommand{\anneeparution}[1]{\def\@ama@annee{#1}}
\def\@ama@pages{}    \newcommand{\pagesarticle}[1]{\def\@ama@pages{#1}}
\def\@ama@issn{}     \newcommand{\issn}[1]{\def\@ama@issn{#1}}
\def\@ama@doi{}      \newcommand{\doi}[1]{\def\@ama@doi{#1}}
\def\@ama@droits{Tous droits r\'eserv\'es.}
\newcommand{\droits}[1]{\def\@ama@droits{#1}}

\def\@ama@logo{figures/logo-ama}
\newcommand{\fichierlogo}[1]{\def\@ama@logo{#1}}
\def\@ama@couverture{}
\newcommand{\couverture}[1]{\def\@ama@couverture{#1}}

%------------------------------------------------------------------------------
% 11. METADONNEES DE L'ARTICLE
%------------------------------------------------------------------------------
\def\@ama@titre{\ClassError{ama-article}{Titre manquant : utilisez \string\titre}{}}
\newcommand{\titre}[1]{\def\@ama@titre{#1}\hypersetup{pdftitle={#1}}}
\def\@ama@titrecourt{}
\newcommand{\titrecourt}[1]{\def\@ama@titrecourt{#1}}
\def\@ama@auteurcourt{}
\newcommand{\auteurcourt}[1]{\def\@ama@auteurcourt{#1}}

% --- Auteurs, affiliations, adresses ---
\newcounter{ama@nbauteurs}
\def\@ama@auteurs{}
\def\@ama@affils{}
\def\@ama@emails{}
% \auteur[marqueur]{Prenom NOM}{indices d'affiliation}{adresse@mail}
%   marqueur facultatif : * pour l'auteur correspondant
\newcommand{\auteur}[4][]{%
  \stepcounter{ama@nbauteurs}%
  \ifnum\value{ama@nbauteurs}>1\relax
    \g@addto@macro\@ama@auteurs{, }%
    \g@addto@macro\@ama@emails{, }%
  \fi
  \g@addto@macro\@ama@auteurs{#2\textsuperscript{\,#3\ifx\relax#1\relax\else,#1\fi}}%
  \g@addto@macro\@ama@emails{\href{mailto:#4}{\nolinkurl{#4}} (#2)}%
}
% \affiliation{indice}{Libelle complet}
\newcommand{\affiliation}[2]{%
  \g@addto@macro\@ama@affils{%
    \textsuperscript{#1}\,\textit{#2}\par}%
}
\def\@ama@correspondance{}
\newcommand{\adressecorrespondance}[1]{\def\@ama@correspondance{#1}}

% --- Historique de l'article ---
\def\@ama@recu{}     \newcommand{\recule}[1]{\def\@ama@recu{#1}}
\def\@ama@revise{}   \newcommand{\reviseule}[1]{\def\@ama@revise{#1}}
\def\@ama@accepte{}  \newcommand{\accepteule}[1]{\def\@ama@accepte{#1}}
\def\@ama@enligne{}  \newcommand{\enligneule}[1]{\def\@ama@enligne{#1}}

% --- Cartouche pedagogique (specifique AMA) ---
\def\@ama@encadrant{} \newcommand{\encadrant}[1]{\def\@ama@encadrant{#1}}
\def\@ama@module{}    \newcommand{\module}[1]{\def\@ama@module{#1}}
\def\@ama@niveau{}    \newcommand{\niveau}[1]{\def\@ama@niveau{#1}}
\def\@ama@anneeac{}   \newcommand{\anneeacademique}[1]{\def\@ama@anneeac{#1}}

% --- Resumes, mots-cles, classification ---
\def\@ama@resume{}    \newcommand{\resume}[1]{\def\@ama@resume{#1}}
\def\@ama@abstract{}  \renewcommand{\abstract}[1]{\def\@ama@abstract{#1}}
\def\@ama@motscles{}  \newcommand{\motscles}[1]{\def\@ama@motscles{#1}}
\def\@ama@msc{}       \newcommand{\classificationmsc}[1]{\def\@ama@msc{#1}}

%------------------------------------------------------------------------------
% 12. EN-TETES ET PIEDS DE PAGE
%------------------------------------------------------------------------------
\RequirePackage{fancyhdr}
\RequirePackage{lastpage}

% Ligne de rappel bibliographique, facon "Auteur et al. / Revue vol (annee) pp"
% Premiere page : rappel de la revue seule ; pages suivantes : auteurs + revue
\newcommand{\ama@rappelrevue}{%
  \ifx\@ama@revuecourt\@empty\@ama@revue\else\@ama@revuecourt\fi
  \ifx\@ama@volume\@empty\else\ \@ama@volume\fi
  \ifx\@ama@annee\@empty\else\ (\@ama@annee)\fi
  \ifx\@ama@pages\@empty\else\ \@ama@pages\fi}

\newcommand{\ama@rappel}{%
  \ifx\@ama@auteurcourt\@empty\else\@ama@auteurcourt\ /\ \fi
  \ifx\@ama@revuecourt\@empty\@ama@revue\else\@ama@revuecourt\fi
  \ifx\@ama@volume\@empty\else\ \@ama@volume\fi
  \ifx\@ama@annee\@empty\else\ (\@ama@annee)\fi
  \ifx\@ama@pages\@empty\else\ \@ama@pages\fi}

\fancypagestyle{amacorps}{%
  \fancyhf{}%
  \renewcommand{\headrulewidth}{0pt}%
  \renewcommand{\footrulewidth}{0pt}%
  \fancyhead[RO,LE]{\footnotesize\thepage}%
}

% Premiere page : pas d'en-tete, notes de correspondance en pied
\fancypagestyle{amapremiere}{%
  \fancyhf{}%
  \renewcommand{\headrulewidth}{0pt}%
  \renewcommand{\footrulewidth}{0pt}%
  \fancyfoot[L]{%
    \parbox[b]{\textwidth}{%
      \footnotesize
      \rule{0.32\textwidth}{0.4pt}\par
      \vspace{2pt}
      \ifx\@ama@correspondance\@empty\else
        \textsuperscript{*}\,Adresse de correspondance : \@ama@correspondance\par\fi
      \ifama@anonyme\else
        \textit{Adresses \'electroniques :} \@ama@emails.\par\fi
      \vspace{4pt}
      \ifx\@ama@issn\@empty\else\@ama@issn\ --\ \fi
      \ifx\@ama@annee\@empty\else\copyright\ \@ama@annee\ \fi
      Acad\'emie des Math\'ematiques Appliqu\'ees. \@ama@droits\par
      \ifx\@ama@doi\@empty\else doi:\,\@ama@doi\par\fi
    }}%
}
\pagestyle{amacorps}

\ifama@brouillon
  \RequirePackage{draftwatermark}
  \SetWatermarkText{BROUILLON}
  \SetWatermarkScale{0.85}
  \SetWatermarkLightness{0.95}
\fi

%------------------------------------------------------------------------------
% 13. BANDEAU DE REVUE ET PAGE DE TITRE
%------------------------------------------------------------------------------
% Titres interlettres des blocs de tete ("A R T I C L E   I N F O")
\newcommand{\ama@espace}[1]{%
  \@ifundefined{textls}{\textbf{\footnotesize #1}}%
                       {\textbf{\footnotesize\textls[220]{#1}}}}

% Bandeau : une seule plage grise sur toute la largeur, logo compris.
\newcommand{\ama@bandeau}{%
  \noindent\rule{\textwidth}{0.5pt}\par
  \vspace{1pt}
  \noindent
  \colorbox{AMAband}{%
    \parbox[c][2.0cm][c]{\dimexpr\textwidth-2\fboxsep\relax}{%
      \begin{minipage}[c]{0.21\linewidth}
        \centering
        \IfFileExists{\@ama@logo.png}
          {\includegraphics[width=0.92\linewidth]{\@ama@logo}}
          {\IfFileExists{\@ama@logo.pdf}
            {\includegraphics[width=0.92\linewidth]{\@ama@logo}}
            {\footnotesize\scshape AMA}}%
      \end{minipage}%
      \hfill
      \begin{minipage}[c]{\ifx\@ama@couverture\@empty 0.77\else 0.62\fi\linewidth}
        \centering
        \ifx\@ama@accroche\@empty\else
          {\large \@ama@accroche\par}
          \vspace{7pt}
        \fi
        {\small page de l'AMA :
          \href{\ama@lien}{\nolinkurl{\@ama@site}}\par}
      \end{minipage}%
      \ifx\@ama@couverture\@empty\else
        \hfill
        \begin{minipage}[c]{0.13\linewidth}
          \centering\includegraphics[width=\linewidth]{\@ama@couverture}
        \end{minipage}%
      \fi
    }}%
  \par\vspace{2pt}
  \noindent\rule{\textwidth}{2pt}\par
}

\renewcommand{\maketitle}{%
  \thispagestyle{amapremiere}%
  \begingroup
  \setlength{\parindent}{0pt}%
  \ama@bandeau
  \vspace{16pt}
  % --- Titre ---
  {\LARGE\bfseries\@ama@titre\par}
  \vspace{12pt}
  % --- Auteurs et affiliations ---
  \ifama@anonyme
    {\normalsize\itshape Soumission anonyme, \'evaluation \`a l'aveugle\par}
  \else
    {\large\@ama@auteurs\par}
    \vspace{7pt}
    {\footnotesize\@ama@affils}%
  \fi
  \vspace{10pt}
  \noindent\rule{\textwidth}{0.4pt}\par
  \vspace{8pt}
  % --- Bloc informations / resume, en vis-a-vis ---
  \noindent
  \begin{minipage}[t]{0.30\textwidth}
    \ama@espace{INFORMATIONS}\par
    \vspace{3pt}\rule{\linewidth}{0.4pt}\par
    \vspace{5pt}
    \footnotesize
    \ifx\@ama@motscles\@empty\else
      \textit{Mots-cl\'es :}\par\@ama@motscles\par\fi
    \ifx\@ama@msc\@empty\else
      \vspace{7pt}\textit{Classification MSC 2020 :}\par\@ama@msc\par\fi
    \ifx\@ama@encadrant\@empty\else
      \vspace{7pt}\textit{Encadrement :}\par\@ama@encadrant\par\fi
    \ifx\@ama@module\@empty\else
      \vspace{7pt}\textit{Cadre p\'edagogique :}\par\@ama@module
      \ifx\@ama@niveau\@empty\else\par\@ama@niveau\fi
      \ifx\@ama@anneeac\@empty\else\par\@ama@anneeac\fi\par\fi
  \end{minipage}%
  \hfill
  \begin{minipage}[t]{0.655\textwidth}
    \ama@espace{R\'ESUM\'E}\par
    \vspace{3pt}\rule{\linewidth}{0.4pt}\par
    \vspace{5pt}
    \footnotesize
    \@ama@resume\par
    \ifx\@ama@abstract\@empty\else
      \vspace{6pt}\textit{\@ama@abstract}\par\fi
    \vspace{6pt}
    \hfill\copyright\ \ifx\@ama@annee\@empty\else\@ama@annee\ \fi
      Acad\'emie des Math\'ematiques Appliqu\'ees. \@ama@droits
  \end{minipage}\par
  \vspace{8pt}
  \noindent\rule{0.30\textwidth}{0.4pt}\hfill\rule{0.655\textwidth}{0.4pt}\par
  \vspace{14pt}
  \endgroup
}

%------------------------------------------------------------------------------
% 14. TITRES DE SECTION (numerotation "1.", "2.1." comme chez Elsevier)
%------------------------------------------------------------------------------
\RequirePackage{titlesec}
\renewcommand{\thesection}{\arabic{section}}
\titlelabel{\thetitle.\quad}
\titleformat{\section}{\normalfont\normalsize\bfseries}{\thesection.}{0.6em}{}
\titleformat{\subsection}{\normalfont\normalsize\itshape}{\thesubsection.}{0.6em}{}
\titleformat{\subsubsection}{\normalfont\small\itshape}{\thesubsubsection.}{0.6em}{}
\titlespacing*{\section}{0pt}{2.4ex plus 1ex minus .2ex}{1.2ex plus .2ex}
\titlespacing*{\subsection}{0pt}{2.0ex plus 1ex minus .2ex}{1.0ex plus .2ex}

%------------------------------------------------------------------------------
% 15. ENVIRONNEMENTS MATHEMATIQUES
%------------------------------------------------------------------------------
\newtheoremstyle{amaplain}{7pt}{7pt}{\itshape}{0pt}{\bfseries}{.}{ }{}
\newtheoremstyle{amadef}  {7pt}{7pt}{\normalfont}{0pt}{\bfseries}{.}{ }{}
\newtheoremstyle{amarem}  {7pt}{7pt}{\normalfont\small}{0pt}{\itshape}{.}{ }{}

\theoremstyle{amaplain}
\newtheorem{theoreme}{Th\'eor\`eme}
\newtheorem{proposition}[theoreme]{Proposition}
\newtheorem{lemme}[theoreme]{Lemme}
\newtheorem{corollaire}[theoreme]{Corollaire}
\newtheorem{conjecture}[theoreme]{Conjecture}

\theoremstyle{amadef}
\newtheorem{definition}[theoreme]{D\'efinition}
\newtheorem{exemple}[theoreme]{Exemple}
\newtheorem{hypothese}[theoreme]{Hypoth\`ese}
\newtheorem{probleme}[theoreme]{Probl\`eme}

\theoremstyle{amarem}
\newtheorem{remarque}[theoreme]{Remarque}
\newtheorem{notation}[theoreme]{Notation}

\renewcommand{\proofname}{D\'emonstration}
\newenvironment{demonstration}[1][\proofname]{\begin{proof}[#1]}{\end{proof}}
\renewcommand{\qedsymbol}{$\square$}

\crefname{theoreme}{th\'eor\`eme}{th\'eor\`emes}
\Crefname{theoreme}{Th\'eor\`eme}{Th\'eor\`emes}
\crefname{definition}{d\'efinition}{d\'efinitions}
\Crefname{definition}{D\'efinition}{D\'efinitions}
\crefname{proposition}{proposition}{propositions}
\Crefname{proposition}{Proposition}{Propositions}
\crefname{lemme}{lemme}{lemmes}
\Crefname{lemme}{Lemme}{Lemmes}
\crefname{corollaire}{corollaire}{corollaires}
\Crefname{corollaire}{Corollaire}{Corollaires}
\crefname{remarque}{remarque}{remarques}
\Crefname{remarque}{Remarque}{Remarques}
\crefname{exemple}{exemple}{exemples}
\Crefname{exemple}{Exemple}{Exemples}
\crefname{hypothese}{hypoth\`ese}{hypoth\`eses}
\Crefname{hypothese}{Hypoth\`ese}{Hypoth\`eses}

% Renvois francises pour les objets standards (cleveref est anglais par defaut)
\ifama@english\else
  \crefname{figure}{fig.}{fig.}
  \Crefname{figure}{Fig.}{Fig.}
  \crefname{table}{tableau}{tableaux}
  \Crefname{table}{Tableau}{Tableaux}
  \crefname{equation}{\'equation}{\'equations}
  \Crefname{equation}{\'Equation}{\'Equations}
  \crefname{section}{section}{sections}
  \Crefname{section}{Section}{Sections}
  \crefname{subsection}{section}{sections}
  \Crefname{subsection}{Section}{Sections}
  \crefname{algorithm}{algorithme}{algorithmes}
  \Crefname{algorithm}{Algorithme}{Algorithmes}
  \crefname{lstlisting}{code}{codes}
  \Crefname{lstlisting}{Code}{Codes}
  \crefname{appendix}{annexe}{annexes}
  \Crefname{appendix}{Annexe}{Annexes}
\fi

%------------------------------------------------------------------------------
% 16. ENCADRES SOBRES
%------------------------------------------------------------------------------
\newtcolorbox{encadre}[1][]{%
  enhanced,breakable,colback=AMAfond,colframe=black,
  boxrule=0.4pt,arc=0pt,left=8pt,right=8pt,top=6pt,bottom=6pt,
  fonttitle=\bfseries\small,coltitle=black,colbacktitle=AMAfond,title={#1}}

\newtcolorbox{pointcle}{%
  enhanced,breakable,colback=white,colframe=black,
  boxrule=0pt,leftrule=1.2pt,arc=0pt,left=8pt,right=4pt,top=4pt,bottom=4pt}

%------------------------------------------------------------------------------
% 17. CODE SOURCE ET ALGORITHMES
%------------------------------------------------------------------------------
\lstdefinestyle{ama}{%
  basicstyle=\ttfamily\footnotesize,
  keywordstyle=\bfseries,
  commentstyle=\color{AMAgris}\itshape,
  stringstyle=\color{AMAgris},
  numbers=left,numberstyle=\tiny\color{AMAgris},numbersep=8pt,
  frame=leftline,rulecolor=\color{black},framesep=6pt,
  backgroundcolor=\color{AMAfond},
  breaklines=true,showstringspaces=false,tabsize=2,captionpos=b,
}
\lstset{style=ama}
\renewcommand{\lstlistingname}{Code}

\algrenewcommand\algorithmicrequire{\textbf{Entr\'ees :}}
\algrenewcommand\algorithmicensure{\textbf{Sorties :}}
\algrenewcommand\algorithmicwhile{\textbf{tant que}}
\algrenewcommand\algorithmicdo{\textbf{faire}}
\algrenewcommand\algorithmicend{\textbf{fin}}
\algrenewcommand\algorithmicif{\textbf{si}}
\algrenewcommand\algorithmicthen{\textbf{alors}}
\algrenewcommand\algorithmicelse{\textbf{sinon}}
\algrenewcommand\algorithmicfor{\textbf{pour}}
\algrenewcommand\algorithmicreturn{\textbf{retourner}}
\floatname{algorithm}{Algorithme}

%------------------------------------------------------------------------------
% 18. RACCOURCIS MATHEMATIQUES USUELS
%------------------------------------------------------------------------------
\newcommand{\N}{\mathbb{N}}   \newcommand{\Z}{\mathbb{Z}}
\newcommand{\Q}{\mathbb{Q}}   \newcommand{\R}{\mathbb{R}}
\newcommand{\C}{\mathbb{C}}   \newcommand{\K}{\mathbb{K}}
\newcommand{\Esp}{\mathbb{E}} \newcommand{\Prob}{\mathbb{P}}
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator*{\argmax}{arg\,max}
\DeclareMathOperator{\Var}{Var}
\DeclareMathOperator{\Cov}{Cov}
\DeclareMathOperator{\rang}{rang}
\DeclareMathOperator{\tr}{tr}
\DeclarePairedDelimiter{\abs}{\lvert}{\rvert}
\DeclarePairedDelimiter{\norme}{\lVert}{\rVert}
\newcommand{\dd}{\mathop{}\!\mathrm{d}}
\newcommand{\transpose}[1]{{#1}^{\!\top}}

%------------------------------------------------------------------------------
% 19. SECTIONS NON NUMEROTEES
%------------------------------------------------------------------------------
\newcommand{\remerciements}[1]{%
  \section*{Remerciements}\addcontentsline{toc}{section}{Remerciements}#1}
\newcommand{\declaration}[1]{%
  \section*{D\'eclaration d'originalit\'e}{\small #1\par}}

\endinput
