function escape_html_tag_syntax(text) {
    // Get rid of < and > symbols in order to avoid basic injenctions.
    return text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function get_items() {
    // Get JSON repsonse with array of existing items and create html elements for their representation on the web-page.

    $.get('/api/get_todo_list_items', function(response) {
        if (response.items === null) {
            console.log('response content is none!');
            $('<p id="initial_info">There are no tasks addded. You can use panel above to do it!</p>').appendTo('#tasks_panel');
        } else {
            console.log('response content has items and we can build our list!');
            for (var i=0; i < response.items.length; i++) {
                // $("<li>" + escape_html_tag_syntax(response.items[i]) + "</li>").appendTo('#tasks_list');
                $('<li></li>').html(escape_html_tag_syntax(response.items[i])).appendTo('#tasks_list');
            }

        }
    });
}

function post_new_item() {
    // Function to be triggered when onclick event on save button is triggered.
    // - validate entered in input field data,
    // - send POST to the server resource at /api/add_todo_list_item to save it in session memeory
    // - on success delete initial message "There are no tasks added..." to free space for added item,
    // and clear input on success
    console.log('clicked save button');

    var input_value = $('#add_item_input').val();

    if (input_value === '') {
        // check if entered value is empty and prevent user from submitting it. If yes: show alert and break this function.
        alert('You can save only non-empty text!');
        return;
    }

    $.post('/api/add_todo_list_item', JSON.stringify({'item': input_value }), function() {
        if ($("#initial_info").length) {
            // check if initial_info p exists and remove it after the moment when user adds new item to list
            $("#initial_info").remove();
        }
        //$("<li>" + input_value + "</li>").appendTo('#tasks_list');
        //$('<li></li>').text(input_value).appendTo('#tasks_list'); // Can't use .text() here cause special symbols are not translated with this func. Use .html() instead
        $('<li></li>').html(escape_html_tag_syntax(input_value)).appendTo('#tasks_list');
        $('#add_item_input').val(''); // clear input
        console.log('post success');
    });
}

$(document).ready(function() {
        get_items();
    }
);

