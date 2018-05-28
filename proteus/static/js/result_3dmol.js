

/* Select ID */
function selectID(glviewer,res1,res2){

    glviewer.setStyle({},{line:{color:'grey'},cartoon:{color:'white'}}); /* Cartoon multi-color */
    glviewer.setStyle({resi:res1},{stick:{colorscheme:'whiteCarbon'}}); 
    glviewer.setStyle({resi:res2},{stick:{colorscheme:'whiteCarbon'}}); 
    
    glviewer.zoomTo({chain : "A", resi: [2,3]});  

    glviewer.render();

}

$(document).ready(function(){


    var txt = "https://files.rcsb.org/download/4PTV.pdb";
    
    $.post(txt, function(d) {

        moldata = data = d;

        /* Creating visualization */
        glviewer = $3Dmol.createViewer("pdb", {
            defaultcolors : $3Dmol.rasmolElementColors
        });

        /* Color background */
        glviewer.setBackgroundColor(0xffffff);

        receptorModel = m = glviewer.addModel(data, "pqr");

        /* Type of visualization */
        glviewer.setStyle({},{line:{color:'grey'},cartoon:{color:'white'}}); /* Cartoon multi-color */
        
        /*glviewer.addSurface($3Dmol.SurfaceType, {opacity:0.3});  Surface */

        /* Name of the atoms */
        atoms = m.selectedAtoms({});
        for ( var i in atoms) {
            var atom = atoms[i];
            atom.clickable = true;
            atom.callback = atomcallback;
        }

        glviewer.mapAtomProperties($3Dmol.applyPartialCharges);
        glviewer.zoomTo();
        glviewer.render();
    });


var atomcallback = function(atom, viewer) {
        if (atom.clickLabel === undefined
                || !atom.clickLabel instanceof $3Dmol.Label) {
            atom.clickLabel = viewer.addLabel(atom.resn + " " + atom.resi + " ("+ atom.elem + ")", {
                fontSize : 10,
                position : {
                    x : atom.x,
                    y : atom.y,
                    z : atom.z
                },
                backgroundColor: "black"
            });
            atom.clicked = true;
        }

        //toggle label style
        else {

            if (atom.clicked) {
                var newstyle = atom.clickLabel.getStyle();
                newstyle.backgroundColor = 0x66ccff;

                viewer.setLabelStyle(atom.clickLabel, newstyle);
                atom.clicked = !atom.clicked;
            }
            else {
                viewer.removeLabel(atom.clickLabel);
                delete atom.clickLabel;
                atom.clicked = false;
            }

        }
};



});