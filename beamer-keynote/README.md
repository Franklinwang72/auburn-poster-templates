# beamer-keynote

<a href="../previews/hd/beamer-keynote.jpg"><img src="../previews/hd/beamer-keynote.jpg" width="100%"></a>

<p align="center"><a href="https://github.com/Franklinwang72/auburn-poster-templates/releases/latest/download/beamer-keynote.zip"><img alt="Download ZIP" src="https://img.shields.io/badge/Download-ZIP-2da44e?style=for-the-badge" /></a></p>

## Use (Overleaf)

Upload this folder (New Project → Upload Project) → **Menu → Compiler → LuaLaTeX** → **Recompile**.

## Write your talk

`beamer-keynote.tex` is only your slides — the look lives in `beamerthemeAUkeynote.sty`. It is standard beamer:

```latex
\section{Background}          % gives you a keynote-style break page

\begin{frame}{Frame title}
  \begin{block}{Definition — ...}...\end{block}
  \begin{alertblock}{Theorem (...)}...\end{alertblock}
  \begin{itemize} \item ... \end{itemize}   % also columns, tables, ...
\end{frame}
```

Set pieces: `\bignum{101}{caption}` · `\heroimage{figures/…}` · `\bigequation{…}` · `\statement{…}`/`\kicker{…}`/`\substatement{…}` · `\CYtitleframe` · `\CYclosingframe{qr-url}{qr-label}{contact}`. Title, author, and date are the usual `\title[short]`, `\subtitle`, `\author[short]`, `\date`.

> beamer cannot produce a tagged (PDF/UA) PDF; this deck is accessible by design instead — contrast, structure, bundled fonts.

## License

Theme code MIT · fonts SIL OFL 1.1 (`fonts/OFL-*.txt`) · the Auburn logo is a registered trademark — replace it if you are not affiliated with Auburn.
