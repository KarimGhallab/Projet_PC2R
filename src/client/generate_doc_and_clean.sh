echo "Generating client documentation..."
epydoc --html --output=../../docs/client/ *.py player/*.py dispatcher/*.py communication/*.py communication/threads/*.py

echo "cleaning client"
rm *.pyc player/*.pyc dispatcher/*.pyc communication/*.pyc communication/threads/*.pyc
