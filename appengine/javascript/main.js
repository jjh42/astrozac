// Javascript that powers the main page.

function imageToPng(dataURI, callback)
// Take an dataURI of an Image and calls callback with the result as a png file data URL.
{
    var img;
    console.debug('Converting image to png');
    img = new Image();
    img.onload = function() {
	var canvas = document.createElement("canvas");
	var ctx = canvas.getContext('2d');
	console.debug('Imaged loaded - converting to png');
	ctx.width = img.width; ctx.height = img.height;
	ctx.drawImage(img, 0,0, img.width, img.height);
	callback(canvas.toDataURL('image/png')); // Get the image encoded as a png.
    };
    img.src = dataURI;
}


function uploaderClass()
{
    // We have to wait for all files from a group to be encoded before
    // we start uploading.
    this.skip = function () {
	this.nfiles = this.nfiles - 1;
	this.checkdone();
    }
    this.files = new Array();
    this.add = function (file,dataurl) {
	this.nfiles = this.nfiles - 1;
	this.files.push({'file' : file, 'dataurl' : dataurl});
	this.checkdone()
    }
    this.checkdone = function ()
    {
	if (this.nfiles == 0) {
	    console.debug('All files received');
	    this.upload();
	}
    }
    this.upload = function () {
	console.debug('Uploading ', this.files);
	var xhr = new XMLHttpRequest();
        var upload_form = $('#upload_form');
	xhr.open(upload_form.attr('method'), upload_form.attr('action'), true)
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
	var topBoundary = this.generate_boundary();
	xhr.setRequestHeader('Content-Type', 
			     "multipart/form-data; boundary=\"" + topBoundary + "\"")
        xhr.send(this.build_form_data(topBoundary));
    }

    this.generate_boundary = function() {
        return ('MultiPartFormBoundary' + (new Date()).getTime() + 
	    + Math.random() + Math.random());
    }

    this.build_form_data = function(topBoundary) {
	var formData = '';
	var fileBoundary = this.generate_boundary();
	for (i = 0; i < this.files.length; i++) {
	    var file = this.files[i].file;
	    var dataurl = this.files[i].dataurl;
	    console.debug('Encode', file);
	    var fileContent = dataurl.substring(5);
	    formData += '--' + topBoundary + '\r\n' +
		'Content-Disposition: form-data; name="file"; ' +   
		'filename="' + unescape(encodeURIComponent(file.name)) + '"' +
		'\r\n' + 
		'Content-Type: ' + file.type + '\r\n';
		'Content-Transfer-Encoding: base64 ' + '\r\n\r\n' + 
		fileContent + '\r\n';
	}
	formData += '--' + topBoundary + '--\r\n';// + topBoundary + '--\r\n';
	console.debug('Form data\r\n', formData);
	return formData;
    }
}



function setupFileUpload()
{ // setup the file-uploading part.
    var opts = {
	readAsMap : {'text/*': 'DataURL', 'image/*' : 'DataURL'},
	readAsDefault : 'DataURL',
	on: { 
	beforestart : function(file) {
	    // Filter out avi files.
	    console.debug('beforestart ', file)
	    var type = file.type
	    if(type.length == 0) {
		console.debug('no file type');
		return true;
	    }
	    // Ok - check against a match list
	    if(type.match(/(image\/.*)|(text\/.*)/)) {
		return true;
	    }
	    
	    // Ignore file
	    $.jGrowl('Ignoring file ' + file.name + ' with type ' + type);
	    return false;
	},
	load: function(e,file) {
	    console.debug('load', e, file);
	},
	loadstart: function(e) {
	    console.debug('loadstart', e);
	},
	loadend: function(e, file) {
	    console.debug('loadend', e, file);
	    if (file.type.match(/image\/.*/)) {
		console.debug('Converting image to png');
		imageToPng(e.currentTarget.result, 
			   function(url) {console.debug('Recoded image');
					  file.type = 'image/png';
					  file.name = file.extra.nameNoExtension + '.png';
					  uploader.add(file, url)});
	    }
	    else {
		uploader.add(file, e.currentTarget.result);
	    }
	},
	progress: function(e) {
	    //console.debug('progress',e);
	},
	skip: function(file) {
	    console.debug('skipping file ', file);
	    uploader.skip();
	},
	groupstart: function(group) {
	    nfiles = group.files.length;
	    uploader = new uploaderClass;
	    uploader.nfiles = nfiles; // Key track of how many files to upload.
	    console.debug('Uploading file group with ' + nfiles + ' files');
	},
	groupend: function(group) {
	    console.debug('groupend', group);
	}},
	dragClass: 'drag',	
    };

    $('#fileElement').fileReaderJS(opts);
    $('#dropbox').fileReaderJS(opts);
}

$( function () {
    // add sendAsBinary in Chrome
    if (! XMLHttpRequest.prototype.sendAsBinary) {
	XMLHttpRequest.prototype.sendAsBinary = function(datastr) {
            var data = new ArrayBuffer(datastr.length);
            var ui8a = new Uint8Array(data, 0);
            for (var i=0; i<datastr.length; i++) {
                ui8a[i] = (datastr.charCodeAt(i) & 0xff);
            }
            var bb = new BlobBuilder();
            bb.append(data);
            var blob = bb.getBlob();
            this.send(blob);
	}
    }
    // global onLoad.
    setupFileUpload();
});