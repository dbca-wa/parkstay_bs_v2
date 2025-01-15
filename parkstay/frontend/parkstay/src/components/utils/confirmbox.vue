/**
* confirmBox components
* author: Tawanda Nyakudjga
* date: 9/10/2016
* alertOptions:{
icon:"<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
message:"Are you sure you want to Delete!!!" ,
buttons:[
{
text:"Delete",
event: "delete",
bsColor:"btn-danger",
handler:function(e) {

vm.showAlert();
},
autoclose:true
}
]
}
**/
<template lang="html" id="confirmbox">
    <div :id="confirmModal" class="modal iiifade">
        <div class="modal-dialog modal-sm">
            <div class="modal-content">
                <!-- dialog body -->
                <div class="modal-body">
                    <div class="row">
                        <div :id="icon" class="col-sm-12 text-center" style="font-size:75px; ">
                            <!--icon goes here-->
                        </div>
                        <div class="col-sm-12 text-center">
                            <p :id="text"><!--modal text--></p>
                        </div>
                    </div>
                </div>
                <!-- dialog buttons -->
                <div class="modal-footer">
                    <div class="row">
                        <div class="col-lg-12" :id="buttons">
                            <!--buttons-->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, toRefs } from 'vue';
import { $, bus } from '../../hooks.js'

const props = defineProps({
    options: {
        required: true,
        type: Object
    },
    id: {
        required: true
    },
    cancelText: {
        default: "Cancel"
    }
})

const { options, id, cancelText } = toRefs(props)

const uid = crypto.randomUUID();
const confirmModal = 'confirmModal' + uid
const icon = 'modalIcon' + uid
const text = 'modalText' + uid
const buttons = 'modalButtons' + uid
const eventHandler = Array()

const confirmBox = function (json) {
    const Obj = json;
    const confirmModalElm = $("#" + confirmModal);
    const iconElm = $("#" + icon);
    const textElm = $("#" + text);
    const buttonsElm = ("#" + buttons);
    const passed_id = Obj.id;
    const autoclose = (typeof Obj.autoclose != "undefined") ? Obj.autoclose : true;
    $(iconElm).html(Obj.icon);
    $(textElm).html(Obj.message);
    $(buttonsElm).html("");
    if (typeof Obj.buttons != "undefined") {
        $.each(Obj.buttons, function (i, btn) {
            var eventHandler = (typeof btn.eventHandler != "undefined") ? btn.eventHandler : "@click";
            $(buttonsElm).append("<button type=\"button\" data-click=" + btn.event + " class=\"btn " + btn.bsColor + "\" style='margin-bottom:10px;'>" + btn.text + "</button>");
            $(function () {
                if (passed_id === id.value) {
                    $('button[data-click]').on('click', function () {

                        if ($(this).attr('data-click') == btn.event) {
                            btn.handler();
                        }
                        if (autoclose) {
                            $(confirmModalElm).modal('hide');
                        }
                    });
                }
            })
        });
    }
    $(buttonsElm).append("<button type='button' data-bs-dismiss='modal' class=\"btn btn-default\" style='margin-bottom:10px;'>" + cancelText.value + "</button>");
}

onMounted(function () {
    confirmBox(options.value);
    bus.on('showAlert', function (_id) {
        if (_id === id.value) {
            $("#" + confirmModal).modal('show');
        }
    })
})
</script>

<style scoped>
.modal-body,
.modal-footer {
    background-color: #fff;
    color: #333;
}

.modal-footer .btn+.btn {
    margin-bottom: 10px;
    margin-left: 5px;
}
</style>
