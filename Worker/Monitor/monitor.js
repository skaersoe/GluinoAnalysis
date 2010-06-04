$(document).ready(function() {
    
    

function addWorker (status, id, name, client, cores) {
   var base = $('<div class="' + status + '" id="w'+ id +'"><div class="hostname">' + name + '</div><div class="client">' + client + '</div><div class="cores">cores: ' + cores  +'</div></div>');
   return base;
}

function getWorkers () {
    $.getJSON("/getWorkers", function(data) {
        $("#workers").empty();
        var totalcores = 0;
        if (data){
            for (var i=0; i < data.length; i++) {
                 $("#workers").append(addWorker(data[i][1], data[i][0], data[i][2], data[i][3], data[i][4]));
                 totalcores += data[i][4];
            };
        }
        setCores(totalcores);
    });
}
function setCores (corecount) {
    $("span.totalcores").html(corecount);
}
    
function changeBanner () {
    $("div.freetext").click(function() {
        $(this).unbind();
        var current = $(this).html().replace(/<br>/g, "\n");

        $(this).html("<textarea style='width: 100%; height: 100%;'>" + current + "</textarea>");
        $(this).change(function() {
            var newtext = $("div.freetext textarea").val().replace(/\n/g, "<br>");
            var output = 'json={"freetext" : "' + newtext + '"}';


            $.ajax({ 
                            url: '/addSettings', 
                            type: 'GET', 
                            data: output, 
                            dataType: "json", 
                            contentType: "application/json; charset=utf-8", 
                            beforeSend: function() { }, 
                            success: function(result) { 
                                $("div.freetext").html(newtext);
                                changeBanner();
                            } 
                        });
            
        });
    });
    
}    

    getWorkers();
    var timer = setInterval(function() {getWorkers();}, 5000);
    changeBanner();  
});
