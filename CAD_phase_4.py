var express = require('express');
var cfenv = require('cfenv');
var bodyParser = require('body-parser');
var app = express();
//...

// start server on the specified port and binding host
var port = process.env.PORT || 3000;
app.listen(port, function() {
    console.log("To view your app, open this link in your browser: http://localhost:" + port);
});
//...
Let's see how to define a path and views. The first line of code tells the Express framework to use the public directory to serve our static files, which include any static images and stylesheets we use. The lines that follow tell the app where to find the templates for our views in the src/views directory, and set our view engine to be EJS. In addition, the framework uses the body-parser middleware to expose incoming request data to the app as JSON. In the closing lines of the example, the express app responds to all incoming GET requests to our app URL by rendering the index.ejs view template.


//...
// serve the files out of ./public as our main files
app.use(express.static('public'));
app.set('views', './src/views');
app.set('view engine', 'ejs');
app.use(bodyParser.json());

var title = 'COS Image Gallery Web Application';
// Serve index.ejs
app.get('/', function (req, res) {
  res.render('index', {status: '', title: title});
});

//...
The following figure shows what the index view template when rendered and sent to the browser. If you are using ,nodemon you might have noticed that your browser refreshed when you saved your changes.

Zoom
uploadimageview
Figure 8. Your updated web app by using templates and views for displays
Our view templates share HTML code between the <head>...</head>; tags, so we placed it into a separate include template. This template (head-inc.ejs) contains a scriptlet (a binding for a JavaScript variable) for the page title on line 1. The title variable is set in app.js, and passed in as data for our view template in the line below that. Otherwise, we are simply using some CDN addresses to pull in Bootstrap CSS, Bootstrap JavaScript, and JQuery. Finally, we add a custom static styles.css file from our pubic/stylesheets directory.


<title><%=title%></title>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
      integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u"
      crossorigin="anonymous">
<script src="https://code.jquery.com/jquery-3.1.1.min.js"
        integrity="sha256-hVVnYaiADRTO2PzUGmuLJr8BLUSjGIZsDYGmIJLv2b8="
        crossorigin="anonymous">
</script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"
        integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa"
        crossorigin="anonymous">
</script>

<link rel="stylesheet" href="stylesheets/style.css">

<!DOCTYPE html>
<html>

<head>
    <%- include('head-inc'); %>
</head>

<body>
<ul class="nav nav-tabs">
    <li role="presentation" class="active"><a href="/">Home</a></li>
    <li role="presentation"><a href="/gallery">Gallery</a></li>
</ul>
<div class="container">
    <h2>Upload Image to IBM Cloud Object Storage</h2>
    <div class="row">
        <div class="col-md-12">
            <div class="container" style="margin-top: 20px;">
                <div class="row">

                    <div class="col-lg-8 col-md-8 well">

                        <p class="wellText">Upload your JPG image file here</p>

                        <form method="post" enctype="multipart/form-data" action="/">
                            <p><input class="wellText" type="file" size="100px" name="img-file" /></p>
                            <br/>
                            <p><input class="btn btn-danger" type="submit" value="Upload" /></p>
                        </form>

                        <br/>
                        <span class="notice"><%=status%></span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
</body>

</html>

Show more
Let's take a moment to return to app.js. The example sets up Express routes to handle extra requests that are made to our app. The code for these routing methods are in two files under the ./src/routes directory in your project:

imageUploadRoutes.js: This file handles what happens when the user selects an image and clicks Upload.
galleryRoutes.js: This file handles requests when the user clicks the Gallery tab to request the imageGallery view.

//...
var imageUploadRoutes = require('./src/routes/imageUploadRoutes')(title);
var galleryRouter = require('./src/routes/galleryRoutes')(title);

app.use('/gallery', galleryRouter);
app.use('/', imageUploadRoutes);

//...
Image upload

See the code from imageUploadRoutes.js. We must create an instance of a new express router and name it imageUploadRoutes at the start. Later, we create a function that returns imageUploadRoutes, and assign it to a variable called router. When completed, the function must be exported as a module to make it accessible to the framework and our main code in app.js. Separating our routing logic from the upload logic requires a controller file named galleryController.js. Because that logic is dedicated to processing the incoming request and providing the appropriate response, we put that logic in that function and save it in the ./src/controllers directory.

The instance of the Router from the Express framework is where our imageUploadRoutes is designed to route requests for the root app route ("/") when the HTTP POST method is used. Inside the post method of our imageUploadRoutes, we use middleware from the multer and multer-s3 modules that is exposed by the galleryController as upload. The middleware takes the data and file from our upload form POST, processes it, and runs a callback function. In the callback function we check that we get an HTTP status code of 200, and that we had at least one file in our request object to upload. Based on those conditions, we set the feedback in our status variable and render the index view template with the new status.


var express = require('express');
var imageUploadRoutes = express.Router();
var status = '';

var router = function(title) {

    var galleryController =
        require('../controllers/galleryController')(title);

    imageUploadRoutes.route('/')
    	.post(
    		galleryController.upload.array('img-file', 1), function (req, res, next) {
                if (res.statusCode === 200 && req.files.length > 0) {
                    status = 'uploaded file successfully';
                }
                else {
                    status = 'upload failed';
                }
                res.render('index', {status: status, title: title});
            });

    return imageUploadRoutes;
};

module.exports = router;

Show more
In comparison, the code for the galleryRouter is a model of simplicity. We follow the same pattern that we did with imageUploadRouter and require galleryController on the first line of the function, then set up our route. The main difference is we are routing HTTP GET requests rather than POST, and sending all the output in the response from getGalleryImages, which is exposed by the galleryController on the last line of the example.


var express = require('express');
var galleryRouter = express.Router();

var router = function(title) {

    var galleryController =
        require('../controllers/galleryController')(title);

    galleryRouter.route('/')
        .get(galleryController.getGalleryImages);

    return galleryRouter;
};
module.exports = router;

