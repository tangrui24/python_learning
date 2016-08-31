/**
 * Created by tr on 2016/8/22.
 */
STATUS = [
            {'id': 1, 'text': "在线"},
            {'id': 2, 'text': "下线"}
        ];

BUSINESS = [
            {'id': 1, 'text': "车上会"},
            {'id': 2, 'text': "二手车"},
            {'id': 3, 'text': "大保健"}
        ];

globalCtrlKeyPress = false;

window.onkeydown = function(event){
    if(event && event.keyCode==17){
        window.globalCtrlKeyPress = true;
    }else{
        window.globalCtrlKeyPress = false;
    }
};

window.onkeyup = function (event) {
    if(event && event.keyCode == 17 ){
        window.globalCtrlKeyPress = false;
    }
};

function MultiChange(ths){
    if(window.globalCtrlKeyPress){
        var val = $(ths).val();
        var index = $(ths).parent().index();
        $(ths).parent().parent().nextAll().find("td :checked").each(function(){
           $(this).parent().parent().children().eq(index).children().val(val);
        })
    }
}

function CheckAll(mode, tb) {
    $(tb).children().each(function () {
        var tr = $(this);
        var is_checked = $(this).find(":checkbox").prop("checked");
        if (is_checked) {
        } else {
            $(this).find(":checkbox").prop("checked", true);
            var is_editing = $(mode).hasClass("editing");
            if (is_editing) {
                RowIntoEdit(tr)
            }
        }
    });
}

function CheckReverse(mode, tb){
    var is_editing = $(mode).hasClass("editing");
    if(is_editing){
         $(tb).children().each(function(){
             var tr = $(this);
             var is_checked = $(this).find(":checkbox").prop("checked");
             if (is_checked){
                 $(this).find(":checkbox").prop("checked",false);
                 RowOutEdit(tr)
             }else{
                 $(this).find(":checkbox").prop("checked",true);
                 RowIntoEdit(tr)
             }
         })
    }else{
        $(tb).children().each(function(){
           if($(this).find(":checkbox").prop("checked")){
               $(this).find(":checkbox").prop("checked",false)
           }else{
               $(this).find(":checkbox").prop("checked",true)
           }
        })
    }
}

function CheckCancel(mode, tb){
    $(tb).children().each(function () {
        var tr = $(this);
        var is_checked = $(this).find(":checkbox").prop("checked");
        if (is_checked){
            $(this).find(":checkbox").prop("checked",false);
            var is_editing = $(mode).hasClass("editing");
            if (is_editing){
                RowOutEdit(tr)
            }
        }
    })
}

function EditMode(ths, tb){
    var is_editing = $(ths).hasClass("editing")
    if (is_editing){
        $(ths).text("进入编辑模式");
        $(ths).removeClass("editing");
        $(tb).children().each(function () {
        var tr = $(this);
        var is_checked = $(this).find(":checkbox").prop("checked");
        if (is_checked){
            RowOutEdit(tr);
        }
    })
    }else{
        $(ths).text("退出编辑模式");
        $(ths).addClass("editing");
        $(tb).children().each(function () {
        var tr = $(this);
        var is_checked = $(this).find(":checkbox").prop("checked");
        if (is_checked) {
            RowIntoEdit(tr)
        }
    });
    }

}

function RowIntoEdit(tr){
    tr.children().each(function () {
        var td = $(this);
        if (td.attr("edit") == "true") {
            if(td.attr("edit-type") == "select"){
                var key_dic = window[td.attr("global-key")];
                var select_val = td.attr("select-val");
                select_val = parseInt(select_val);
                var options = "";
                $.each(key_dic, function (index, value) {
                    if(value.id == select_val){
                        options += "<option selected='selected'>" + value.text + "</option>";
                    }else{
                        options += "<option>"+ value.text +"</option>"
                    }
                });
                var temp = "<select onchange='MultiChange(this)'>" + options + "</select>";
                td.html(temp)
            }else{
                var text = td.text();
                var temp = "<input type='text' value='" + text + "'/>";
                td.html(temp);
            }
        }
    })
}

function RowOutEdit(tr){
    tr.children().each(function () {
        var td = $(this);
        if(td.attr("edit") == "true"){
            var inp_val = $(this).children(":first").val();
            td.text(inp_val)
        }
    })
}

 $(function(){
     $("#tb1").find(":checkbox").click(function(){
         var tr = $(this).parent().parent();
         var isEditing = $("#edit_mode").hasClass("editing");
         if(isEditing){
             if($(this).prop("checked")){
                 RowIntoEdit(tr);
             }else{
                 RowOutEdit(tr);
             }
         }
     });
 });
