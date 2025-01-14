System.register([],(function(e,t){"use strict";return{execute:function(){e({detectOverflow:ve,popperGenerator:We});var t=e("top","top"),n=e("bottom","bottom"),r=e("right","right"),o=e("left","left"),i=e("auto","auto"),a=e("basePlacements",[t,n,r,o]),s=e("start","start"),f=e("end","end"),c=e("clippingParents","clippingParents"),p=e("viewport","viewport"),u=e("popper","popper"),l=e("reference","reference"),d=e("variationPlacements",a.reduce((function(e,t){return e.concat([t+"-"+s,t+"-"+f])}),[])),m=e("placements",[].concat(a,[i]).reduce((function(e,t){return e.concat([t,t+"-"+s,t+"-"+f])}),[])),h=e("beforeRead","beforeRead"),v=e("read","read"),g=e("afterRead","afterRead"),y=e("beforeMain","beforeMain"),b=e("main","main"),w=e("afterMain","afterMain"),x=e("beforeWrite","beforeWrite"),O=e("write","write"),j=e("afterWrite","afterWrite"),E=e("modifierPhases",[h,v,g,y,b,w,x,O,j]);function D(e){return e?(e.nodeName||"").toLowerCase():null}function A(e){if(null==e)return window;if("[object Window]"!==e.toString()){var t=e.ownerDocument;return t&&t.defaultView||window}return e}function P(e){return e instanceof A(e).Element||e instanceof Element}function L(e){return e instanceof A(e).HTMLElement||e instanceof HTMLElement}function W(e){return"undefined"!=typeof ShadowRoot&&(e instanceof A(e).ShadowRoot||e instanceof ShadowRoot)}var M=e("applyStyles",{name:"applyStyles",enabled:!0,phase:"write",fn:function(e){var t=e.state;Object.keys(t.elements).forEach((function(e){var n=t.styles[e]||{},r=t.attributes[e]||{},o=t.elements[e];L(o)&&D(o)&&(Object.assign(o.style,n),Object.keys(r).forEach((function(e){var t=r[e];!1===t?o.removeAttribute(e):o.setAttribute(e,!0===t?"":t)})))}))},effect:function(e){var t=e.state,n={popper:{position:t.options.strategy,left:"0",top:"0",margin:"0"},arrow:{position:"absolute"},reference:{}};return Object.assign(t.elements.popper.style,n.popper),t.styles=n,t.elements.arrow&&Object.assign(t.elements.arrow.style,n.arrow),function(){Object.keys(t.elements).forEach((function(e){var r=t.elements[e],o=t.attributes[e]||{},i=Object.keys(t.styles.hasOwnProperty(e)?t.styles[e]:n[e]).reduce((function(e,t){return e[t]="",e}),{});L(r)&&D(r)&&(Object.assign(r.style,i),Object.keys(o).forEach((function(e){r.removeAttribute(e)})))}))}},requires:["computeStyles"]});function k(e){return e.split("-")[0]}var B=Math.max,H=Math.min,R=Math.round;function S(){var e=navigator.userAgentData;return null!=e&&e.brands&&Array.isArray(e.brands)?e.brands.map((function(e){return e.brand+"/"+e.version})).join(" "):navigator.userAgent}function T(){return!/^((?!chrome|android).)*safari/i.test(S())}function V(e,t,n){void 0===t&&(t=!1),void 0===n&&(n=!1);var r=e.getBoundingClientRect(),o=1,i=1;t&&L(e)&&(o=e.offsetWidth>0&&R(r.width)/e.offsetWidth||1,i=e.offsetHeight>0&&R(r.height)/e.offsetHeight||1);var a=(P(e)?A(e):window).visualViewport,s=!T()&&n,f=(r.left+(s&&a?a.offsetLeft:0))/o,c=(r.top+(s&&a?a.offsetTop:0))/i,p=r.width/o,u=r.height/i;return{width:p,height:u,top:c,right:f+p,bottom:c+u,left:f,x:f,y:c}}function q(e){var t=V(e),n=e.offsetWidth,r=e.offsetHeight;return Math.abs(t.width-n)<=1&&(n=t.width),Math.abs(t.height-r)<=1&&(r=t.height),{x:e.offsetLeft,y:e.offsetTop,width:n,height:r}}function C(e,t){var n=t.getRootNode&&t.getRootNode();if(e.contains(t))return!0;if(n&&W(n)){var r=t;do{if(r&&e.isSameNode(r))return!0;r=r.parentNode||r.host}while(r)}return!1}function N(e){return A(e).getComputedStyle(e)}function I(e){return["table","td","th"].indexOf(D(e))>=0}function F(e){return((P(e)?e.ownerDocument:e.document)||window.document).documentElement}function U(e){return"html"===D(e)?e:e.assignedSlot||e.parentNode||(W(e)?e.host:null)||F(e)}function z(e){return L(e)&&"fixed"!==N(e).position?e.offsetParent:null}function _(e){for(var t=A(e),n=z(e);n&&I(n)&&"static"===N(n).position;)n=z(n);return n&&("html"===D(n)||"body"===D(n)&&"static"===N(n).position)?t:n||function(e){var t=/firefox/i.test(S());if(/Trident/i.test(S())&&L(e)&&"fixed"===N(e).position)return null;var n=U(e);for(W(n)&&(n=n.host);L(n)&&["html","body"].indexOf(D(n))<0;){var r=N(n);if("none"!==r.transform||"none"!==r.perspective||"paint"===r.contain||-1!==["transform","perspective"].indexOf(r.willChange)||t&&"filter"===r.willChange||t&&r.filter&&"none"!==r.filter)return n;n=n.parentNode}return null}(e)||t}function X(e){return["top","bottom"].indexOf(e)>=0?"x":"y"}function Y(e,t,n){return B(e,H(t,n))}function G(e){return Object.assign({},{top:0,right:0,bottom:0,left:0},e)}function J(e,t){return t.reduce((function(t,n){return t[n]=e,t}),{})}var K=e("arrow",{name:"arrow",enabled:!0,phase:"main",fn:function(e){var i,s=e.state,f=e.name,c=e.options,p=s.elements.arrow,u=s.modifiersData.popperOffsets,l=k(s.placement),d=X(l),m=[o,r].indexOf(l)>=0?"height":"width";if(p&&u){var h=function(e,t){return G("number"!=typeof(e="function"==typeof e?e(Object.assign({},t.rects,{placement:t.placement})):e)?e:J(e,a))}(c.padding,s),v=q(p),g="y"===d?t:o,y="y"===d?n:r,b=s.rects.reference[m]+s.rects.reference[d]-u[d]-s.rects.popper[m],w=u[d]-s.rects.reference[d],x=_(p),O=x?"y"===d?x.clientHeight||0:x.clientWidth||0:0,j=b/2-w/2,E=h[g],D=O-v[m]-h[y],A=O/2-v[m]/2+j,P=Y(E,A,D),L=d;s.modifiersData[f]=((i={})[L]=P,i.centerOffset=P-A,i)}},effect:function(e){var t=e.state,n=e.options.element,r=void 0===n?"[data-popper-arrow]":n;null!=r&&("string"!=typeof r||(r=t.elements.popper.querySelector(r)))&&C(t.elements.popper,r)&&(t.elements.arrow=r)},requires:["popperOffsets"],requiresIfExists:["preventOverflow"]});function Q(e){return e.split("-")[1]}var Z={top:"auto",right:"auto",bottom:"auto",left:"auto"};function $(e){var i,a=e.popper,s=e.popperRect,c=e.placement,p=e.variation,u=e.offsets,l=e.position,d=e.gpuAcceleration,m=e.adaptive,h=e.roundOffsets,v=e.isFixed,g=u.x,y=void 0===g?0:g,b=u.y,w=void 0===b?0:b,x="function"==typeof h?h({x:y,y:w}):{x:y,y:w};y=x.x,w=x.y;var O=u.hasOwnProperty("x"),j=u.hasOwnProperty("y"),E=o,D=t,P=window;if(m){var L=_(a),W="clientHeight",M="clientWidth";L===A(a)&&"static"!==N(L=F(a)).position&&"absolute"===l&&(W="scrollHeight",M="scrollWidth"),(c===t||(c===o||c===r)&&p===f)&&(D=n,w-=(v&&L===P&&P.visualViewport?P.visualViewport.height:L[W])-s.height,w*=d?1:-1),c!==o&&(c!==t&&c!==n||p!==f)||(E=r,y-=(v&&L===P&&P.visualViewport?P.visualViewport.width:L[M])-s.width,y*=d?1:-1)}var k,B=Object.assign({position:l},m&&Z),H=!0===h?function(e,t){var n=e.x,r=e.y,o=t.devicePixelRatio||1;return{x:R(n*o)/o||0,y:R(r*o)/o||0}}({x:y,y:w},A(a)):{x:y,y:w};return y=H.x,w=H.y,d?Object.assign({},B,((k={})[D]=j?"0":"",k[E]=O?"0":"",k.transform=(P.devicePixelRatio||1)<=1?"translate("+y+"px, "+w+"px)":"translate3d("+y+"px, "+w+"px, 0)",k)):Object.assign({},B,((i={})[D]=j?w+"px":"",i[E]=O?y+"px":"",i.transform="",i))}var ee=e("computeStyles",{name:"computeStyles",enabled:!0,phase:"beforeWrite",fn:function(e){var t=e.state,n=e.options,r=n.gpuAcceleration,o=void 0===r||r,i=n.adaptive,a=void 0===i||i,s=n.roundOffsets,f=void 0===s||s,c={placement:k(t.placement),variation:Q(t.placement),popper:t.elements.popper,popperRect:t.rects.popper,gpuAcceleration:o,isFixed:"fixed"===t.options.strategy};null!=t.modifiersData.popperOffsets&&(t.styles.popper=Object.assign({},t.styles.popper,$(Object.assign({},c,{offsets:t.modifiersData.popperOffsets,position:t.options.strategy,adaptive:a,roundOffsets:f})))),null!=t.modifiersData.arrow&&(t.styles.arrow=Object.assign({},t.styles.arrow,$(Object.assign({},c,{offsets:t.modifiersData.arrow,position:"absolute",adaptive:!1,roundOffsets:f})))),t.attributes.popper=Object.assign({},t.attributes.popper,{"data-popper-placement":t.placement})},data:{}}),te={passive:!0},ne=e("eventListeners",{name:"eventListeners",enabled:!0,phase:"write",fn:function(){},effect:function(e){var t=e.state,n=e.instance,r=e.options,o=r.scroll,i=void 0===o||o,a=r.resize,s=void 0===a||a,f=A(t.elements.popper),c=[].concat(t.scrollParents.reference,t.scrollParents.popper);return i&&c.forEach((function(e){e.addEventListener("scroll",n.update,te)})),s&&f.addEventListener("resize",n.update,te),function(){i&&c.forEach((function(e){e.removeEventListener("scroll",n.update,te)})),s&&f.removeEventListener("resize",n.update,te)}},data:{}}),re={left:"right",right:"left",bottom:"top",top:"bottom"};function oe(e){return e.replace(/left|right|bottom|top/g,(function(e){return re[e]}))}var ie={start:"end",end:"start"};function ae(e){return e.replace(/start|end/g,(function(e){return ie[e]}))}function se(e){var t=A(e);return{scrollLeft:t.pageXOffset,scrollTop:t.pageYOffset}}function fe(e){return V(F(e)).left+se(e).scrollLeft}function ce(e){var t=N(e),n=t.overflow,r=t.overflowX,o=t.overflowY;return/auto|scroll|overlay|hidden/.test(n+o+r)}function pe(e){return["html","body","#document"].indexOf(D(e))>=0?e.ownerDocument.body:L(e)&&ce(e)?e:pe(U(e))}function ue(e,t){var n;void 0===t&&(t=[]);var r=pe(e),o=r===(null==(n=e.ownerDocument)?void 0:n.body),i=A(r),a=o?[i].concat(i.visualViewport||[],ce(r)?r:[]):r,s=t.concat(a);return o?s:s.concat(ue(U(a)))}function le(e){return Object.assign({},e,{left:e.x,top:e.y,right:e.x+e.width,bottom:e.y+e.height})}function de(e,t,n){return t===p?le(function(e,t){var n=A(e),r=F(e),o=n.visualViewport,i=r.clientWidth,a=r.clientHeight,s=0,f=0;if(o){i=o.width,a=o.height;var c=T();(c||!c&&"fixed"===t)&&(s=o.offsetLeft,f=o.offsetTop)}return{width:i,height:a,x:s+fe(e),y:f}}(e,n)):P(t)?function(e,t){var n=V(e,!1,"fixed"===t);return n.top=n.top+e.clientTop,n.left=n.left+e.clientLeft,n.bottom=n.top+e.clientHeight,n.right=n.left+e.clientWidth,n.width=e.clientWidth,n.height=e.clientHeight,n.x=n.left,n.y=n.top,n}(t,n):le(function(e){var t,n=F(e),r=se(e),o=null==(t=e.ownerDocument)?void 0:t.body,i=B(n.scrollWidth,n.clientWidth,o?o.scrollWidth:0,o?o.clientWidth:0),a=B(n.scrollHeight,n.clientHeight,o?o.scrollHeight:0,o?o.clientHeight:0),s=-r.scrollLeft+fe(e),f=-r.scrollTop;return"rtl"===N(o||n).direction&&(s+=B(n.clientWidth,o?o.clientWidth:0)-i),{width:i,height:a,x:s,y:f}}(F(e)))}function me(e,t,n,r){var o="clippingParents"===t?function(e){var t=ue(U(e)),n=["absolute","fixed"].indexOf(N(e).position)>=0&&L(e)?_(e):e;return P(n)?t.filter((function(e){return P(e)&&C(e,n)&&"body"!==D(e)})):[]}(e):[].concat(t),i=[].concat(o,[n]),a=i[0],s=i.reduce((function(t,n){var o=de(e,n,r);return t.top=B(o.top,t.top),t.right=H(o.right,t.right),t.bottom=H(o.bottom,t.bottom),t.left=B(o.left,t.left),t}),de(e,a,r));return s.width=s.right-s.left,s.height=s.bottom-s.top,s.x=s.left,s.y=s.top,s}function he(e){var i,a=e.reference,c=e.element,p=e.placement,u=p?k(p):null,l=p?Q(p):null,d=a.x+a.width/2-c.width/2,m=a.y+a.height/2-c.height/2;switch(u){case t:i={x:d,y:a.y-c.height};break;case n:i={x:d,y:a.y+a.height};break;case r:i={x:a.x+a.width,y:m};break;case o:i={x:a.x-c.width,y:m};break;default:i={x:a.x,y:a.y}}var h=u?X(u):null;if(null!=h){var v="y"===h?"height":"width";switch(l){case s:i[h]=i[h]-(a[v]/2-c[v]/2);break;case f:i[h]=i[h]+(a[v]/2-c[v]/2)}}return i}function ve(e,o){void 0===o&&(o={});var i=o,s=i.placement,f=void 0===s?e.placement:s,d=i.strategy,m=void 0===d?e.strategy:d,h=i.boundary,v=void 0===h?c:h,g=i.rootBoundary,y=void 0===g?p:g,b=i.elementContext,w=void 0===b?u:b,x=i.altBoundary,O=void 0!==x&&x,j=i.padding,E=void 0===j?0:j,D=G("number"!=typeof E?E:J(E,a)),A=w===u?l:u,L=e.rects.popper,W=e.elements[O?A:w],M=me(P(W)?W:W.contextElement||F(e.elements.popper),v,y,m),k=V(e.elements.reference),B=he({reference:k,element:L,strategy:"absolute",placement:f}),H=le(Object.assign({},L,B)),R=w===u?H:k,S={top:M.top-R.top+D.top,bottom:R.bottom-M.bottom+D.bottom,left:M.left-R.left+D.left,right:R.right-M.right+D.right},T=e.modifiersData.offset;if(w===u&&T){var q=T[f];Object.keys(S).forEach((function(e){var o=[r,n].indexOf(e)>=0?1:-1,i=[t,n].indexOf(e)>=0?"y":"x";S[e]+=q[i]*o}))}return S}function ge(e,t){void 0===t&&(t={});var n=t,r=n.placement,o=n.boundary,i=n.rootBoundary,s=n.padding,f=n.flipVariations,c=n.allowedAutoPlacements,p=void 0===c?m:c,u=Q(r),l=u?f?d:d.filter((function(e){return Q(e)===u})):a,h=l.filter((function(e){return p.indexOf(e)>=0}));0===h.length&&(h=l);var v=h.reduce((function(t,n){return t[n]=ve(e,{placement:n,boundary:o,rootBoundary:i,padding:s})[k(n)],t}),{});return Object.keys(v).sort((function(e,t){return v[e]-v[t]}))}var ye=e("flip",{name:"flip",enabled:!0,phase:"main",fn:function(e){var a=e.state,f=e.options,c=e.name;if(!a.modifiersData[c]._skip){for(var p=f.mainAxis,u=void 0===p||p,l=f.altAxis,d=void 0===l||l,m=f.fallbackPlacements,h=f.padding,v=f.boundary,g=f.rootBoundary,y=f.altBoundary,b=f.flipVariations,w=void 0===b||b,x=f.allowedAutoPlacements,O=a.options.placement,j=k(O),E=m||(j!==O&&w?function(e){if(k(e)===i)return[];var t=oe(e);return[ae(e),t,ae(t)]}(O):[oe(O)]),D=[O].concat(E).reduce((function(e,t){return e.concat(k(t)===i?ge(a,{placement:t,boundary:v,rootBoundary:g,padding:h,flipVariations:w,allowedAutoPlacements:x}):t)}),[]),A=a.rects.reference,P=a.rects.popper,L=new Map,W=!0,M=D[0],B=0;B<D.length;B++){var H=D[B],R=k(H),S=Q(H)===s,T=[t,n].indexOf(R)>=0,V=T?"width":"height",q=ve(a,{placement:H,boundary:v,rootBoundary:g,altBoundary:y,padding:h}),C=T?S?r:o:S?n:t;A[V]>P[V]&&(C=oe(C));var N=oe(C),I=[];if(u&&I.push(q[R]<=0),d&&I.push(q[C]<=0,q[N]<=0),I.every((function(e){return e}))){M=H,W=!1;break}L.set(H,I)}if(W)for(var F=function(e){var t=D.find((function(t){var n=L.get(t);if(n)return n.slice(0,e).every((function(e){return e}))}));if(t)return M=t,"break"},U=w?3:1;U>0&&"break"!==F(U);U--);a.placement!==M&&(a.modifiersData[c]._skip=!0,a.placement=M,a.reset=!0)}},requiresIfExists:["offset"],data:{_skip:!1}});function be(e,t,n){return void 0===n&&(n={x:0,y:0}),{top:e.top-t.height-n.y,right:e.right-t.width+n.x,bottom:e.bottom-t.height+n.y,left:e.left-t.width-n.x}}function we(e){return[t,r,n,o].some((function(t){return e[t]>=0}))}var xe=e("hide",{name:"hide",enabled:!0,phase:"main",requiresIfExists:["preventOverflow"],fn:function(e){var t=e.state,n=e.name,r=t.rects.reference,o=t.rects.popper,i=t.modifiersData.preventOverflow,a=ve(t,{elementContext:"reference"}),s=ve(t,{altBoundary:!0}),f=be(a,r),c=be(s,o,i),p=we(f),u=we(c);t.modifiersData[n]={referenceClippingOffsets:f,popperEscapeOffsets:c,isReferenceHidden:p,hasPopperEscaped:u},t.attributes.popper=Object.assign({},t.attributes.popper,{"data-popper-reference-hidden":p,"data-popper-escaped":u})}}),Oe=e("offset",{name:"offset",enabled:!0,phase:"main",requires:["popperOffsets"],fn:function(e){var n=e.state,i=e.options,a=e.name,s=i.offset,f=void 0===s?[0,0]:s,c=m.reduce((function(e,i){return e[i]=function(e,n,i){var a=k(e),s=[o,t].indexOf(a)>=0?-1:1,f="function"==typeof i?i(Object.assign({},n,{placement:e})):i,c=f[0],p=f[1];return c=c||0,p=(p||0)*s,[o,r].indexOf(a)>=0?{x:p,y:c}:{x:c,y:p}}(i,n.rects,f),e}),{}),p=c[n.placement],u=p.x,l=p.y;null!=n.modifiersData.popperOffsets&&(n.modifiersData.popperOffsets.x+=u,n.modifiersData.popperOffsets.y+=l),n.modifiersData[a]=c}}),je=e("popperOffsets",{name:"popperOffsets",enabled:!0,phase:"read",fn:function(e){var t=e.state,n=e.name;t.modifiersData[n]=he({reference:t.rects.reference,element:t.rects.popper,strategy:"absolute",placement:t.placement})},data:{}}),Ee=e("preventOverflow",{name:"preventOverflow",enabled:!0,phase:"main",fn:function(e){var i=e.state,a=e.options,f=e.name,c=a.mainAxis,p=void 0===c||c,u=a.altAxis,l=void 0!==u&&u,d=a.boundary,m=a.rootBoundary,h=a.altBoundary,v=a.padding,g=a.tether,y=void 0===g||g,b=a.tetherOffset,w=void 0===b?0:b,x=ve(i,{boundary:d,rootBoundary:m,padding:v,altBoundary:h}),O=k(i.placement),j=Q(i.placement),E=!j,D=X(O),A="x"===D?"y":"x",P=i.modifiersData.popperOffsets,L=i.rects.reference,W=i.rects.popper,M="function"==typeof w?w(Object.assign({},i.rects,{placement:i.placement})):w,R="number"==typeof M?{mainAxis:M,altAxis:M}:Object.assign({mainAxis:0,altAxis:0},M),S=i.modifiersData.offset?i.modifiersData.offset[i.placement]:null,T={x:0,y:0};if(P){if(p){var V,C="y"===D?t:o,N="y"===D?n:r,I="y"===D?"height":"width",F=P[D],U=F+x[C],z=F-x[N],G=y?-W[I]/2:0,J=j===s?L[I]:W[I],K=j===s?-W[I]:-L[I],Z=i.elements.arrow,$=y&&Z?q(Z):{width:0,height:0},ee=i.modifiersData["arrow#persistent"]?i.modifiersData["arrow#persistent"].padding:{top:0,right:0,bottom:0,left:0},te=ee[C],ne=ee[N],re=Y(0,L[I],$[I]),oe=E?L[I]/2-G-re-te-R.mainAxis:J-re-te-R.mainAxis,ie=E?-L[I]/2+G+re+ne+R.mainAxis:K+re+ne+R.mainAxis,ae=i.elements.arrow&&_(i.elements.arrow),se=ae?"y"===D?ae.clientTop||0:ae.clientLeft||0:0,fe=null!=(V=null==S?void 0:S[D])?V:0,ce=F+ie-fe,pe=Y(y?H(U,F+oe-fe-se):U,F,y?B(z,ce):z);P[D]=pe,T[D]=pe-F}if(l){var ue,le="x"===D?t:o,de="x"===D?n:r,me=P[A],he="y"===A?"height":"width",ge=me+x[le],ye=me-x[de],be=-1!==[t,o].indexOf(O),we=null!=(ue=null==S?void 0:S[A])?ue:0,xe=be?ge:me-L[he]-W[he]-we+R.altAxis,Oe=be?me+L[he]+W[he]-we-R.altAxis:ye,je=y&&be?function(e,t,n){var r=Y(e,t,n);return r>n?n:r}(xe,me,Oe):Y(y?xe:ge,me,y?Oe:ye);P[A]=je,T[A]=je-me}i.modifiersData[f]=T}},requiresIfExists:["offset"]});function De(e,t,n){void 0===n&&(n=!1);var r,o,i=L(t),a=L(t)&&function(e){var t=e.getBoundingClientRect(),n=R(t.width)/e.offsetWidth||1,r=R(t.height)/e.offsetHeight||1;return 1!==n||1!==r}(t),s=F(t),f=V(e,a,n),c={scrollLeft:0,scrollTop:0},p={x:0,y:0};return(i||!i&&!n)&&(("body"!==D(t)||ce(s))&&(c=(r=t)!==A(r)&&L(r)?{scrollLeft:(o=r).scrollLeft,scrollTop:o.scrollTop}:se(r)),L(t)?((p=V(t,!0)).x+=t.clientLeft,p.y+=t.clientTop):s&&(p.x=fe(s))),{x:f.left+c.scrollLeft-p.x,y:f.top+c.scrollTop-p.y,width:f.width,height:f.height}}function Ae(e){var t=new Map,n=new Set,r=[];function o(e){n.add(e.name),[].concat(e.requires||[],e.requiresIfExists||[]).forEach((function(e){if(!n.has(e)){var r=t.get(e);r&&o(r)}})),r.push(e)}return e.forEach((function(e){t.set(e.name,e)})),e.forEach((function(e){n.has(e.name)||o(e)})),r}var Pe={placement:"bottom",modifiers:[],strategy:"absolute"};function Le(){for(var e=arguments.length,t=new Array(e),n=0;n<e;n++)t[n]=arguments[n];return!t.some((function(e){return!(e&&"function"==typeof e.getBoundingClientRect)}))}function We(e){void 0===e&&(e={});var t=e,n=t.defaultModifiers,r=void 0===n?[]:n,o=t.defaultOptions,i=void 0===o?Pe:o;return function(e,t,n){void 0===n&&(n=i);var o,a,s={placement:"bottom",orderedModifiers:[],options:Object.assign({},Pe,i),modifiersData:{},elements:{reference:e,popper:t},attributes:{},styles:{}},f=[],c=!1,p={state:s,setOptions:function(n){var o="function"==typeof n?n(s.options):n;u(),s.options=Object.assign({},i,s.options,o),s.scrollParents={reference:P(e)?ue(e):e.contextElement?ue(e.contextElement):[],popper:ue(t)};var a,c,l=function(e){var t=Ae(e);return E.reduce((function(e,n){return e.concat(t.filter((function(e){return e.phase===n})))}),[])}((a=[].concat(r,s.options.modifiers),c=a.reduce((function(e,t){var n=e[t.name];return e[t.name]=n?Object.assign({},n,t,{options:Object.assign({},n.options,t.options),data:Object.assign({},n.data,t.data)}):t,e}),{}),Object.keys(c).map((function(e){return c[e]}))));return s.orderedModifiers=l.filter((function(e){return e.enabled})),s.orderedModifiers.forEach((function(e){var t=e.name,n=e.options,r=void 0===n?{}:n,o=e.effect;if("function"==typeof o){var i=o({state:s,name:t,instance:p,options:r}),a=function(){};f.push(i||a)}})),p.update()},forceUpdate:function(){if(!c){var e=s.elements,t=e.reference,n=e.popper;if(Le(t,n)){s.rects={reference:De(t,_(n),"fixed"===s.options.strategy),popper:q(n)},s.reset=!1,s.placement=s.options.placement,s.orderedModifiers.forEach((function(e){return s.modifiersData[e.name]=Object.assign({},e.data)}));for(var r=0;r<s.orderedModifiers.length;r++)if(!0!==s.reset){var o=s.orderedModifiers[r],i=o.fn,a=o.options,f=void 0===a?{}:a,u=o.name;"function"==typeof i&&(s=i({state:s,options:f,name:u,instance:p})||s)}else s.reset=!1,r=-1}}},update:(o=function(){return new Promise((function(e){p.forceUpdate(),e(s)}))},function(){return a||(a=new Promise((function(e){Promise.resolve().then((function(){a=void 0,e(o())}))}))),a}),destroy:function(){u(),c=!0}};if(!Le(e,t))return p;function u(){f.forEach((function(e){return e()})),f=[]}return p.setOptions(n).then((function(e){!c&&n.onFirstUpdate&&n.onFirstUpdate(e)})),p}}e("createPopper",We({defaultModifiers:[ne,je,ee,M,Oe,ye,Ee,K,xe]}))}}}));
//# sourceMappingURL=index-legacy.js.map