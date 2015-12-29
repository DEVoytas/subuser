# -*- coding: utf-8 -*-

#external imports
#import
#internal imports
import subuserlib.verify

def getInstalledImagesThatAreInUse(user):
  """
  Returns a dictionary of currently installed images that are currently used by a subsuser directly, or indirectly (as a dependency of another image).

  Returns {imageId(string) : InstalledImage}
  """
  installedImagesThatAreInUse = {} # {imageId : installedImage}
  for _,subuser in user.getRegistry().getSubusers().items():
    if subuser.getImageId():
      for inUseInstalledImage in subuser.getUser().getInstalledImages()[subuser.getImageId()].getImageLineage():
        installedImagesThatAreInUse[inUseInstalledImage.getImageId()] = inUseInstalledImage
  return installedImagesThatAreInUse

def removeOldImages(user,dryrun,sourceRepoId=None,imageSourceName=None):
  installedImagesThatAreInUse = getInstalledImagesThatAreInUse(user)
  for installedImageId,installedImage in user.getInstalledImages().items():
    filterOut = False
    # If a sourceRepoId or sourceImageId have been specified, only remove images from that repo/soure
    if sourceRepoId:
      filterOut = True
      if installedImage.getSourceRepoId() == sourceRepoId:
        filterOut = False
        if imageSourceName:
          filterOut = True
          if installedImage.getImageSourceName() == imageSourceName:
            filterOut = False
    if not installedImageId in installedImagesThatAreInUse and not filterOut:
      user.getRegistry().log("Removing unneeded image "+installedImage.getImageId() + " : " + installedImage.getImageSource().getIdentifier())
      if not dryrun:
        installedImage.removeCachedRuntimes()
        installedImage.removeDockerImage()
  if not dryrun:
    subuserlib.verify.verify(user)
    user.getRegistry().commit()
