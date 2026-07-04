.PHONY: main clean distclean
main:            # build the poster (LuaLaTeX via latexmkrc)
	latexmk
clean:           # remove build files, keep the PDF
	latexmk -c
distclean:       # remove build files AND the PDF
	latexmk -C
