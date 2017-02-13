function post_login_credentials() {
    // Function to be run when onclick event on save button is triggered.
    // - validate entered in input field data,
    // - send POST to the server resource at /api/add_todo_list_item to save it in session memory
    // - on success delete initial message "There are no tasks added..." to free space for added item,
    // and clear input on success
    console.log("clicked log me in button");

    var login_input_value = $("#login_input").val();
    var password_input_value = $("#password_input").val();

    if ((login_input_value === "") || (password_input_value === "")) {
        // check if entered value is empty and prevent user from submitting it. If yes: show alert and break this function.
        alert("You can submit only non-empty values!");
        return;
    }

    // $.post('/api/post_login_credentials', JSON.stringify({'login': login_input_value, 'password': password_input_value}), function() {
    //    console.log('post success');
    //});

    $.ajax({url: "/api/post_login_credentials",
            data: JSON.stringify({"login": login_input_value, "password": password_input_value}),
            type: "POST",
            success: function() {
                console.log("login success");
                sessionStorage.setItem("username", login_input_value);
                $( location ).attr("href", "/todo_list");
            },
            error: function() {
                alert("Wrong login or password.");
            },
            });
}

$(document).ready(function() {
    }
);
