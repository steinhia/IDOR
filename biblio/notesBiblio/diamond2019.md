***

# Reduced White Matter Fiber Density in Autism Spectrum Disorder
 
## Resume 
* Differences in brain networks and underlying white matter abnormalities have been suggested to underlie symptoms of autism spectrum disorder (ASD).
* “fixels” (specific fiber-bundle populations within a voxel)
* analytic technique that calculates structural metrics specific to differently-oriented fixels
* individuals with ASD had reduced FD (fiber density), suggestive of decreased axonal count, in several major white matter tracts, including the corpus callosum (CC), bilateral inferior frontal-occipital fasciculus, right arcuate fasciculus, and right uncinate fasciculus, as well as a GWM reduction. 
*  lower FD in the splenium of the CC was associated with greater social impairment.
* Our findings suggest that reduced FD (fiber density) could be the primary microstructural white matter abnormality in ASD.
 
## Introduction 
* TD : structural properties of white matter tracts associated with social skills -> structural alterations related to ASD ??
* DTI : decreased FA and increased MD (Di2018..) in many structures including CC
* zikopoulos2010 : axonal density may be reduced
* variability in DTI findings : maybe due to methodological chellenges of DTI -> only one direction per voxel
    * the inability to resolve multiple fiber orientations in regions of crossing/kissing fiber geometry may contribute to unreliable estimates of FA and MD in these regions (Jeurissen et al. 2013). 
* CSD (Constrained Spherical Deconvolution) permet de distinguer plusieurs populations (directions) de fibres dans un voxel.
  * décompose le signal de diffusion capté dans chaque voxel, modèle sphérique pour estimer les directions principales (déconvolution)
  * FOD : fiber orientation distribution (intensité pour chaque orientation dans chaque voxel)
 
## Etude 
* hyp : 
  * (1) ASD would have reduced fiber density in areas associated with social behavior and 
  * (2) reduced FD would correlate with social impairment
* Mesures : 
  * FD fiber density : integrale FOD dans une direction (un fixel) = quantité de fibres dans cette direction
  * FC fiber cross-section : épaisseur du faisceau (déformation nécessaire pour aligner avec un template)
  * FDC fiber density and cross-section : product
  * GWM-FD : Global white matter fiber density (dans tout le cerveau)
* Probabilistic tractography : uses DWI measures to build a map of brain fibers
* SIFT (Spherical-deconvolution informed filtering of tractograms) -> filter non-relevant fibers
* used ROI -> defined by fixel and voxel masks

## Results
* ASD : decreased FD in CC in the splenium/genu, no FA or MD difference
* decreased GWD-FD, même si plus petite diff que le CC -> generalized disorder ?
* negative correlation social impairment / fiber density in the CC splenium (other measures not significant)
 
## Discussion 
* reduced axonal density ?
* reduction in axonal count = global property
* no differences in FA/MD -> FBA more sensitive ?
 
