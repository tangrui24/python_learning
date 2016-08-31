/**
 * Created by Administrator on 2016/6/1.
 */

function deleted_selected(){
    var ID = [];
    var select_true = "False";
    $(".select_options").click(function(){
    var select = $("select[name='action']").children("option:selected");
    var selected_value = select.val();
    if(selected_value != '-------'){

        var brothers = $("input:checked").parent().siblings();
        brothers.each(function(){
            if ($(this).attr('name') == "id"){
                var tmp = $(this).children("a").text();
                ID.push(tmp);
                select_true = "True"
            }
        });

        if (select_true == "True"){
            var base_url=window.location.pathname;
            var jsondata = JSON.stringify({'id':ID});
            $.ajax({
                type:"POST",
                url: base_url,
                data:{'data':jsondata},
                success:function(arg){
                    if (arg == "True"){
                        alert("操作成功");
                        window.location.reload()
                    }
                    else {
                        alert("操作失败")
                    }
                },
                error:function(arg){
                    alert("操作失败")
                }
                })
        }}
        })
}

function all_selected(){
    $(".all_selected").click(function(){
        if ($(".all_selected").prop("checked") == true) {
            $("input[type='checkbox']").prop("checked", true)
        }
        else{
            $("input[type='checkbox']").prop("checked", false)
        }
    })
}

function Auto_search(){
    $(".AutoSearch").keyup(function(){
        var search_data = JSON.stringify({'search':$(".AutoSearch").val()});
        var base_url=window.location.pathname;
        $.ajax({
            type:'POST',
            url:base_url,
            data: {"data":search_data},
            success:function(arg){
                console.log(arg.length);
                if (arg){
                    $("tbody").remove(); //移除tbody 重新排列查询的数据
                    var args = eval(arg); //将后端返回的json数据生成对象
                    $("table").append("<tbody></tbody>");
                    for( var line in args){
                        var val = "<tr id =" + line +"><td><input type='checkbox'></td></tr>"; //格式化添加的内容
                        $("table tbody").append(val);
                        var pd = "tbody tr" + "#"+line;
                        var value = args[line];
                        $(pd).append(value)
                        }
                }
                else{
                    console.log("null")
                    }
                }
        })
})
}

$(function(){
    deleted_selected();
    all_selected();
    Auto_search();
});