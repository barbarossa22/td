function escape_html_tag_syntax(text) {
    // Get rid of < and > symbols in order to avoid basic injenctions.
    return text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function get_items() {
    // Get JSON repsonse with array of existing items and their category, and then create html elements for their representation on the web-page.
    var selected_chboxes_objs_list = $("#category_checkboxes").find("input:checkbox:checked");
    var lst = []
    selected_chboxes_objs_list.map(function(index, item) {
            lst.push(item.value);
        });

    $.get("/api/get_todo_list_items", function(response) {
        $("#tasks_list").empty();

        if (response.items === null) {
            if ($("#initial_info").length == 0) {
                $('<p id="initial_info">There are no tasks addded. You can use panel above to do it!</p>').appendTo('#tasks_panel');
            }
        } else {
            console.log("Response content has items and we can build our list!");
            for (var i=response.items.length-1; i>-1; i--) {
                // if category in selected_chboxes_list append, no - good bye
                if ($.inArray(response.items[i].category, lst) == -1) {
                    console.log("No such category in the list of selected by user categories to view.");
                }
                else {
                    var li = $(`<li data-id=${response.items[i].id}></li>`).html(escape_html_tag_syntax(response.items[i].item_value));
                    li.toggleClass(`${response.items[i].category}_li`);
                    li.appendTo("#tasks_list");
                }
            }
        }
    });
}



function post_new_item() {
    // Function to be run when onclick event on save button is triggered.
    // - validate entered in input field data,
    // - send POST to the server resource at /api/add_todo_list_item to save it in session memory
    // - on success delete initial message "There are no tasks added..." to free space for added item,
    // and clear input on success
    var input_value = $("#add_item_input").val();

    if (input_value === "") {
        // check if entered value is empty and prevent user from submitting it. If yes: show alert and break this function.
        alert("You can save only non-empty text!");
        return;
    }
    var category_name=$("#item_category_rbtns").find("input:radio[name='categories']:checked")[0].value;
    $.post("/api/add_todo_list_item", JSON.stringify({"item_value": input_value, "category": category_name }), function() {
        $("#add_item_input").val(""); // clear input
        if ($("#initial_info").length) {
            // check if initial_info p exists and remove it after the moment when user adds new item to list
            $("#initial_info").remove();
        }
        $("#tasks_list").empty();
        get_items()
    });
}

function draw_logout_btn() {
    // if login in sessionStorage prepend logout button to #main:
    var username = sessionStorage.getItem("username");
    if (username) {
        var template = `<p class="text-right">Logged in as <em>${username}</em>. <a href="/logout" onclick="sessionStorage.removeItem('username');"><span class="fa fa-sign-out"></span>Logout</a></p>`
        $("#main").prepend(template);
    }
}

function show_removal_modal(item_to_remove) {

    var text = item_to_remove.text();
    var id = item_to_remove.data("id");
    var modal = $('#myModal');

    var p = $("<p></p>");
    p.text(`Are you sure you want to remove "${text}" item?`);
    $(".modal-content").prepend(p);

    modal.css('display', 'block');

    $("#close_modal").off().on("click", function(event) {
        modal.css("display", "none");
        p.remove();
        });

    $("#submit_modal").off().on("click", function(event) {

        $.post("/api/remove_item", JSON.stringify({"id": id}), function() {
            item_to_remove.remove();
            get_items();
        });

        p.remove();
        modal.css("display", "none");
    });
}


$(document).ready(function() {
        draw_logout_btn();
        get_items();

        $("#tasks_list").on("click", "li", function(event) {
            show_removal_modal($(this));
            return false;
        });
    }
);
