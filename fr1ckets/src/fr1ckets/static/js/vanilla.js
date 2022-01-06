document.addEventListener('DOMContentLoaded', function(event) {
    var sitebody = document.querySelector("#js_container");
    var warning = document.querySelector("#js_warning");
    sitebody.classList.remove("hidden");
    warning.classList.add("hidden");

    // Open descriptions in modal
    document.querySelectorAll('.js_desclink').forEach(item => {
        item.addEventListener('click', event => {
            event.preventDefault();
            let myhref = event.target.href.split("#");
            let toshow = document.querySelector("#"+myhref[1])
            toshow.classList.remove("visuallyhidden");
            document.querySelector("body").classList.add("noscroll");
        })
    });

    // Open images in modal
    document.querySelectorAll('.product--image').forEach(item => {
        item.addEventListener('click', event => {
            event.preventDefault();

            let mysrc = event.target.src;
            let myalt = event.target.alt;

            let modal = document.querySelector("#large_image");

            modal.querySelector(".image").src = mysrc;
            modal.querySelector(".image").alt = myalt;

            modal.classList.remove("visuallyhidden");
            document.querySelector("body").classList.add("noscroll");
        })
    });

    // Close modal and re-enable scrolling
    document.querySelectorAll('.js_modalclose').forEach(item => {
        item.addEventListener('click', event => { 
             document.querySelectorAll('.modalwrapper').forEach(wrapper => {
                console.log(wrapper);
                hideclass = wrapper.getAttribute("data-hideclass");
                wrapper.classList.add(hideclass);
            });
            document.querySelector("body").classList.remove("noscroll");
        });
    });

    // Bestelling nakijken
    document.querySelector("#check_button").addEventListener('click', event => {
        event.preventDefault();
        document.querySelector("#order_overview").classList.remove("hidden");
    });


});


