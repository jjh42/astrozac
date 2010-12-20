// Javascript that powers the main page.

function setupFileUpload()
{ // setup the file-uploading part.
    $('.upload').fileUploadUI({
        uploadTable: $('.upload_files'),
        downloadTable: $('.download_files'),
        buildUploadRow: function (files, index) {
            var file = files[index];
            return $(
                '<tr style="display:none">' +
                '<td>' + file.name + '<\/td>' +
                '<td class="file_upload_progress"><div><\/div><\/td>' +
                '<td class="file_upload_cancel">' +
                '<div class="ui-state-default ui-corner-all ui-state-hover" title="Cancel">' +
                '<span class="ui-icon ui-icon-cancel"><\/span>' +
                '<\/div>' +
                '<\/td>' +
                '<\/tr>'
            );
        },
        buildDownloadRow: function (file) {
            return $(
                '<tr style="display:none"><td>' + file.name + '<\/td><\/tr>'
            );
        }
    });

    $('.upload').fileUpload.drop = function() {console.debug('Hello')};
}

$( function () {
    // global onLoad.
    setupFileUpload();
});