var activeSpan = null;
var previousZIndex = "";
var dragging = false;
var dirtySpans = new Array();
var outQueue = new Array();
var checkpointFrequency = 1500;
var ZINDEX_TOP = 255;
var ZINDEX_SPAN_MAX = 150;

// session and login management
var clientKey = "";
var sessionId = "";
var sessionKey = "";

$(document).ready(function () {
    $("#toolbox").hide();
    $("#resizetool").hide();
    $("#windowbar").hide();

    // get the page content/notes    
    getNotesContent();
    
    // start the checkpoint
    setTimeout(checkpoint, checkpointFrequency);
    
    // Generalized onClick handler.  Delegates click events to the target handler.
    $(document).on("click", function(evt) {
        if (!dragging) {
            processOnClick(evt);
        }
        
        // intentionally consuming the click handler
        return false;
    });
    
    // Generalized key handler.
    $(document).on("keypress", function(evt) {
        if (activeSpan) {
            // tweak down for border size . . .
            // . . . won't resize in Firefox.
            if (activeSpan.scrollHeight - 2 > parseInt(activeSpan.style.height)) {
                activeSpan.style.height = activeSpan.scrollHeight + "px";
                attachToolbox(activeSpan);
            }
            
            addDirtySpan(activeSpan);
        }
        
        return true;
    });
    
    $("#windowbar").on("mousedown", function(evt) {
console.log("mousedown - entered mousedown handler");            
        dragging = true;
console.log("mousedown - dragging");

        // workaround for chrome/FF
        var offsetX = evt.offsetX ? evt.offsetX : evt.originalEvent.layerX;
        var offsetY = evt.offsetY ? evt.offsetY : evt.originalEvent.layerY;
        
        $("#windowbar").on("mousemove", function(evt) {
            if (activeSpan && dragging) {
                var newX = evt.pageX - offsetX;
                var newY = evt.pageY + parseInt($("#windowbar").get(0).style.height) - offsetY - 2;
                activeSpan.style.left = newX + "px";
                activeSpan.style.top = newY + "px";
            
                // reattach the toolbox
                attachToolbox(activeSpan);
                
                // mark the span dirty
                addDirtySpan(activeSpan);
            }
        });
        
        $("#windowbar").on("mouseup", function(evt) {
console.log("mouseup - stopping drag");                
            dragging = false;
            // unattach mousemove and mouseup
            $("#windowbar").off("mousemove");
            $("#windowbar").off("mouseup");
            
            return false;
        });
        
        $("#windowbar").on("mouseout", function(evt) {
console.log("mouseout - stopping drag");                
            dragging = false;
            // unattach mousemove and mouseup
            $("#windowbar").off("mousemove");
            $("#windowbar").off("mouseup");
            
            return false;
        });
        
console.log("mousedown - exiting handler");            
        return false;
    });

    
    $("#resizebox").on("mousedown", function(evt) {
console.log("resize - entered mousedown handler");            
        dragging = true;
console.log("resize - dragging");

        // workaround for chrome/FF
        var offsetX = evt.offsetX ? evt.offsetX : evt.originalEvent.layerX;
        var offsetY = evt.offsetY ? evt.offsetY : evt.originalEvent.layerY;
        
        $("#resizebox").on("mousemove", function(evt) {
console.log(evt);
            if (activeSpan && dragging) {
console.log('OffsetX ' + offsetX + "  offsetY " + offsetY);
                activeSpan.style.width = (evt.pageX - parseInt(activeSpan.style.left) - offsetX - 2) + "px";
                activeSpan.style.height = (evt.pageY - parseInt(activeSpan.style.top) - offsetY - 2) + "px";
                $("#windowbar").get(0).style.width = activeSpan.style.width;
                
                // reattach the toolbox
                attachToolbox(activeSpan);

                // mark the span dirty
                addDirtySpan(activeSpan);
            }
        });
        
        $("#resizebox").on("mouseup", function(evt) {
//console.log("resizebox - stopping drag");                
            dragging = false;
            // unattach mousemove and mouseup
            $("#resizebox").off("mousemove");
            $("#resizebox").off("mouseup");
            
            return false;
        });
        
        $("#resizebox").on("mouseout", function(evt) {
//console.log("resizebox - stopping drag");                
            dragging = false;
            // unattach mousemove and mouseup
            $("#resizebox").off("mousemove");
            $("#resizebox").off("mouseup");
            
            return false;
        });
        
//console.log("resizebox - exiting handler");            
        return false;
    });


    // bind keystrokes
    /*
    $(document).keypress(function (evt) {
        console.log("keypress focusElement: " + focusElement);
        if (focusElement != null) {
            var code = String.fromCharCode(evt.charCode);
            focusElement.innerHTML += code;
        }
    });
    */
});

var createContentSpan = function createContentSpan(spanId, x, y, width, height, zIndex) {
    var span = $('<span/>', {
        id: spanId,
        style: 'display: inline; position: fixed; left: ' + x + '; top: ' + y + '; width: ' + width + '; height: ' + height + '; background-color: #ccc; z-index: ' + zIndex + ';',
        contenteditable: 'true'
    });
    
    span.appendTo("body");
    
    $(span).on("mouseenter", hoverSpan);
    $(span).on("mouseleave", unhoverSpan);
    
    return span;
}

var createSpan = function createSpan(evt) {
console.log("entered createSpan");        
console.log(evt);
    if (!dragging) {
        // reset any other active span
        if (activeSpan) {
            deactivateSpan(activeSpan);
        }
        
        var dt = new Date();
        var spanId = "content" + dt.getTime();

        var sp = createContentSpan(spanId, evt.clientX + "px", evt.clientY + "px", "300px", "300px", 0);
        
        // create the new div
        createdSpan = $("#" + sp.get(0).id).get(0);
console.log("createdSpan - " + createdSpan.id);            
        activeSpan = sp[0];
        activateSpan(createdSpan);
    }
}

var reloadSpan = function reloadSpan(values) {
    if (values.zIndex > ZINDEX_SPAN_MAX) {
        values.zIndex = ZINDEX_SPAN_MAX;
    }

    var sp = createContentSpan(values.id, values.left, values.top, values.width, values.height, values.zIndex);
    sp.html(values.html);
}

var hoverSpan = function hoverSpan(evt) {
    // find the content span parent
    var target = evt.target;
    var targetId = target.id;
    
    target.style.border = "1px dashed #333";
}

var unhoverSpan = function unhoverSpan(evt) {
    var target = evt.target;
    var targetId = target.id;
    
    evt.target.style.border = "none";
}

function deactivateSpan(activeSpan) {
    if (activeSpan) {
        // reset the active span
        activeSpan.style.backgroundColor = "#eee";
        activeSpan.contentEditable = "false";
        $("#toolbox").hide();
        activeSpan.style.zIndex = previousZIndex;
    }
}

function activateSpan(activeSpan) {
    if (activeSpan) {
        previousZIndex = activeSpan.style.zIndex;
        activeSpan.contentEditable = "true";
        activeSpan.style.backgroundColor = "#ccc";
        activeSpan.style.zIndex = ZINDEX_SPAN_MAX;
        activeSpan.focus();
        
        // attach the toolbox to the text box
        attachToolbox(activeSpan);
    }
}

function attachToolbox(activeSpan) {
    if (activeSpan) {
        $("#toolbox").show();
        $("#toolbox").get(0).style.left = parseInt(activeSpan.style.left) + parseInt(activeSpan.style.width) + "px";
        $("#toolbox").get(0).style.top = activeSpan.style.top;
        
        $("#resizetool").show();
        $("#resizetool").get(0).style.left = parseInt(activeSpan.style.left) + parseInt(activeSpan.style.width) + "px";
        $("#resizetool").get(0).style.top = parseInt(activeSpan.style.top) + parseInt(activeSpan.style.height) + "px";
        
        $("#windowbar").show();
        $("#windowbar").get(0).style.left = parseInt(activeSpan.style.left) + "px";
        $("#windowbar").get(0).style.top = parseInt(activeSpan.style.top) - parseInt($("#windowbar").get(0).style.height) + "px";
        var dt = new Date(parseInt(activeSpan.id.substring(7)));
        $("#windowtitle").html(dt.toString());
    }
}

function tagSelection(tag) {
    if (activeSpan && window.getSelection) {
        var selection = window.getSelection();
        document.execCommand(tag, false, selection);
    }
}

function addDirtySpan(activeSpan) {
    if (activeSpan) {
        var spanId = activeSpan.id;
        if (dirtySpans.indexOf(spanId) < 0) {
            dirtySpans.push(spanId);
        }
    }        
}

var checkpoint = function checkpoint() {
    if (dirtySpans.length > 0) {
        //console.log("Checkpointing");
        dirtySpans.forEach(spanToJson);
        dirtySpans.length = 0;
    }
    
    if (outQueue.length > 0) {
        console.log(outQueue);
        // write the output queue to the server
        postNotesContent();
    }
    
    setTimeout(checkpoint, checkpointFrequency);
}

var spanToJson = function spanToJason(spId) {
    if (spId) {
        var sp = $("#" + spId).get(0);
        console.log(sp);
        var out = {
            "top": sp.style.top,
            "left": sp.style.left,
            "height": sp.style.height,
            "width": sp.style.width,
            "id": sp.id,
            "html": $("#" + spId).html(),
            "zIndex": sp.style.zIndex
        };
        
        // zIndex:  should be sp.style.zIndex when spId is not activeSpan ID
        
        //console.log(out);
        outQueue.push(out);
    }
}

/* ********************
 * ***** event handling
 * ********************/
function processOnClick(evt) {
    var target = evt.target;
    var targetId = target.id;
    
    // pass clicks made on the icons to the parent container
    if (targetId === "windowtitle") {
        target = $("#windowbar").get(0);
    } else if (targetId === "boldicon") {
        target = $("#boldbox").get(0);
    } else if (targetId === "italicicon") {
        target = $("#italicbox").get(0);
    } else if (targetId === "underlineicon") {
        target = $("#underlinebox").get(0);
    } else if (targetId === "promoteicon") {
        target = $("#promotebox").get(0);
    } else if (targetId === "demoteicon") {
        target = $("#removebox").get(0);
    } else if (targetId === "feedicon") {
        target = $("#feedbox").get(0);
    } else if (targetId === "deleteicon") {
        target = $("#deletebox").get(0);
    } else if (targetId === "resizeicon") {
        target = $("#resizebox").get(0);
    }

    // yeah, do it again
    targetId = target.id;

    // act on specific IDs
    if (targetId === "boldbox") {
        boldText();
    } else if (targetId === "italicbox") {
        italicizeText();
    } else if (targetId === "underlinebox") {
        underlineText();
    } else if (targetId === "promotebox") {
        promoteSpan();
    } else if (targetId === "demotebox") {
        demoteSpan();
    } else if (targetId === "feedbox") {
        displayPermalink();
    } else if (targetId === "deletebox") {
console.log("deletebox, activespan is " + activeSpan);
        deleteSpan();
    }
    
    // login button
    if (targetId === "loginButton") {
        performLogin($("#login_username").val(), $("#login_password").val());
    }
    
    // other IDs aren't handled by click (like the resize box)
    
    // check to see if we need to activate a span
    if (targetId.indexOf("content") == 0) {
        deactivateSpan(activeSpan);
        
        activeSpan = target;
        
        activateSpan(activeSpan);
    }
    
    // finally, check to see if we need to create a span
    // this is because the targetId is undefined/empty string
    if (!targetId) {
        createSpan(evt);
    }
}

/* ****************
   ***** formatting
   ****************/
var boldText = function boldText() {
    if (activeSpan != null) {
        tagSelection("bold");
    }
}

var italicizeText = function italicizeText() {
    if (activeSpan != null) {
        tagSelection("italic");
            
        // mark the span dirty
        addDirtySpan(activeSpan);
    }
}

var underlineText = function underlineText() {
    if (activeSpan != null) {
        tagSelection("underline");                    

        // mark the span dirty
        addDirtySpan(activeSpan);
    }
}

/* ***********************
 * ***** span manipulation
 * ***********************/

var promoteSpan = function promoteSpan() {
    if (activeSpan != null && previousZIndex < ZINDEX_SPAN_MAX) {
        previousZIndex += 1;

        // mark the span dirty
        addDirtySpan(activeSpan);
    }
}

var demoteSpan = function demoteSpan() {
    if (activeSpan != null) {
        previousZIndex -= 1;

        // mark the span dirty
        addDirtySpan(activeSpan);
    }
}

var displayPermalink = function displayPermalink() {
    if (activeSpan != null) {
        console.log(window.getSelection());
    }
}

var deleteSpan = function deleteSpan() {
    if (activeSpan != null) {
console.log("deleting span ", activeSpan.id);
        // delete the active span
        deleteNote();

        // we could also promote another span...
        $("#" + activeSpan.id).remove();
        $("#windowbar").hide();
        $("#toolbox").hide();
        $("#resizetool").hide();
    }
}

/* *************
 * ***** network
 * *************/
var getNotesContent = function getNotesContent() {
    // TODO shoud I clear the content spans first?
    // get the content
    // user ids
    var requestData = createJsonRequest(sessionId, clientKey, sessionKey, {});
    $.ajax({
        url: "index.py/content",
        type: "GET",
        data: "",
        dataType: "json",
        headers: {
            "X-PAD-SESSION-ID": requestData.sessionId,
            "X-PAD-REQUEST-HASH": requestData.requestHash
        },
        success: function(data) {
            console.log(data);
            var results = data.results;
            if (results === "OK") {
                for (var i = 0; i < data.notes.length; i++) {
                    reloadSpan(data.notes[i]);
                }
            } else if (results === "LOGIN") {
                // display the login popover
                $("#login").show();
            }
        },
        error: function(data) {
            console.log("error: " + data);
        }
    });
}

var postNotesContent = function postNotesContent() {
    var requestData = createJsonRequest(sessionId, clientKey, sessionKey, outQueue);
    $.ajax({
        url: "index.py/checkpoint",
        type: "POST",
        data: JSON.stringify(requestData.request),
        dataType: "json",
        headers: {
            "X-PAD-SESSION-ID": requestData.sessionId,
            "X-PAD-REQUEST-HASH": requestData.requestHash
        },
        success: function(data) {
            if (data.results === "OK") {
                outQueue.length = 0;
                console.log("checkpointed: ", data);
            } else if (data.results === "LOGIN") {
                // display the login popover
                $("#login").show();
            }
        },
        error: function(data) {
            outQueue.length = 0;
        }
    });
}

var deleteNote = function deleteNote() {
    var blob = {
        "spanId": activeSpan.id
    };
    var requestData = createJsonRequest(sessionId, clientKey, sessionKey, blob);
    $.ajax({
        url: "index.py/delete/" + activeSpan.id,
        type: "DELETE",
        data: JSON.stringify(requestData.request),
        dataType: "json",
        headers: {
            "X-PAD-SESSION-ID": requestData.sessionId,
            "X-PAD-REQUEST-HASH": requestData.requestHash
        },
        success: function(data) {
            if (results === "OK") {
                console.log("deleted: ", data);
            } else if (results === "LOGIN") {
                // display the login popover
                $("#login").show();
            }
        },
        error: function(data) {
            console.log("error: ", data);
        }
    });

}

var performLogin = function performLogin(username, password) {
    if (username && password) {
        // one time client key
        clientKey = createClientKey();
        
        // hash the password
        var hashedPassword = passwordHash(password);
        
        var loginRequest = {
            "username": username,
            "password": hashedPassword,
            "clientKey": clientKey
        };
        
        $.ajax({
            url: "index.py/login",
            type: "POST",
            data: JSON.stringify(loginRequest),
            dataType: "json",
            success: function(data) {
                if (data.results === "OK") {
                    // get the session key and id
                    sessionKey = data.sessionKey;
                    sessionId = data.sessionId;
                    // clear any existing login failure message
                    $("#login_message").html("");
                    $("#login").hide();
                    // load the page content
                    getNotesContent();
                } else if (data.results === "LOGIN") {
                    // display the login popover
                    $("#login").show();
                } else if (data.results === "FAILED") {
                    // display the login popover
                    $("#login").show();
                    // display the login failure message
                    $("#login_message").html("Login failed.  Please check your username and password.");
                }
            },
            error: function(data) {
                console.log("error: " + data);
            }
        });
    } else {
        $("#login_message").html("Can't log in:  missing username or password");
    }
}

/* ***************
 * ***** utilities
 * ***************/

function AssertException(message) { this.message = message; }
AssertException.prototype.toString = function () {
    return 'AssertException: ' + this.message;
}
    
function assert(exp, message) {
    if (!exp) {
        throw new AssertException(message);
    }
}

