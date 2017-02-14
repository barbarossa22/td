function post_login_credentials() {
    // Function to be run when onclick event on "log me in" button is triggered.
    // - send POST to the server resource at /api/post_login_credentials.
    // - on success redirect user to /todo_list page,
    // - on failure read the status code and if 401 inform user that credentials are wrong,
    // or inform him that there are server-side issues.

    console.log("clicked log me in button");

    var login_input_value = $("#login_input").val();
    var password_input_value = $("#password_input").val();

    if ((login_input_value === "") || (password_input_value === "")) {
        // check if entered value is empty and prevent user from submitting it. If yes: show alert and break this function.
        alert("You can submit only non-empty values!");
        return;
    }

    $.ajax({url: "/api/post_login_credentials",
            data: JSON.stringify({"login": login_input_value, "password": password_input_value}),
            type: "POST",
            success: function() {
                console.log("login success");
                sessionStorage.setItem("username", login_input_value);
                $( location ).attr("href", "/todo_list");
            },
            error: function(xhr) {
                // When 401 unauthorized comes throw a message about wrong credentials, otherwise inform that server is dead.
                if (xhr.status == 401) {
                alert("Wrong login or password.");
                } else {
                alert("Something went wrong on the server.")
                }
            },
            });
}

$(document).ready(function() {
    }
);
