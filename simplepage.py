'''A simple program to create an html file froma given string,
and call the default web browser to display the file.'''

def main():
    browseLocal()


def browseLocal(filename='spotifyhtml.html'):
    '''Start your webbrowser on a local file containing the text
    with given filename.'''
    import webbrowser, os.path
    webbrowser.open("file:///" + os.path.abspath(filename)) #elaborated for Mac

from flask import Flask
app = Flask(__name__)
 
@app.route("/")
@app.route("/<title><artist>")
def spotify(title=None, artist=None):
    return render_template('spotifyhtml.html', title=title, artist=artist)
 

if __name__ == "__main__":
	app.run()
	# main()