# -*- coding: cp1252 -*-
import json
import math

def gameClock(millis): # returns a string in the "12:34" format of the game clock.
    negative = millis < 0
    time_seconds,time_minutes = math.modf(abs(millis) / 1000.0 / 60.0)
    time_seconds = int(math.floor(time_seconds * 60.0))
    if time_seconds < 10:
        time_seconds = "0" + str(time_seconds)
    else:
        time_seconds = str(time_seconds)

    if negative:
        return "-" + str(int(time_minutes)) + ":" + time_seconds
    else:
        return str(int(time_minutes)) + ":" + time_seconds


# counts[version][type][champion][item/champion_stats][item_stats]
counts = json.load(open("stats.json"))

# stats[version][pool][champion][item][stat]
stats = {"5.11":{}, "5.14":{}}
for version in stats:
    stats[version] = {"normal":{"all":{}},"ranked":{"all":{}},"all":{"all":{}}}

# item_pickRate = item_builderCount / mageCount for selected champion in selected pool
# item_sellRate = item_sellerCount / item_builderCount for selected champion in selected pool
# item_buildTime = item_buildTimeSum / item_builderCount for selected champion in selected pool
# item_priorityScore = item_priorityScoreSum / item_builderCount for selected champion in selected pool
for versionKey in counts:
    for typeKey in counts[versionKey]:
        allChampsMageCount = 0.0
        allChampsCount = 0.0
        allChampsBuilderCounts = {}
        allChampsSellerCounts = {}
        allChampsBuildTimeSums = {}
        allChampsPriorityScoreSums = {}
        for champKey in counts[versionKey][typeKey]:
            if champKey not in stats[versionKey][typeKey]:
                stats[versionKey][typeKey][champKey] = {}
            
            mageCount = 1.0 * counts[versionKey][typeKey][champKey]["mageCount"]
            totalCount = 1.0 * counts[versionKey][typeKey][champKey]["totalCount"]
            allChampsMageCount += mageCount
            allChampsCount += totalCount
            for itemKey in counts[versionKey][typeKey][champKey]:
                if itemKey not in {"mageCount","totalCount"}:
                    builderCount = 1.0* counts[versionKey][typeKey][champKey][itemKey]["builderCount"]
                    sellerCount = 1.0 * counts[versionKey][typeKey][champKey][itemKey]["sellerCount"]
                    buildTimeSum = 1.0 * counts[versionKey][typeKey][champKey][itemKey]["buildTimeSum"]
                    priorityScoreSum = 1.0 * counts[versionKey][typeKey][champKey][itemKey]["priorityScoreSum"]
                    for allDict in [allChampsBuilderCounts, allChampsSellerCounts, allChampsBuildTimeSums, allChampsPriorityScoreSums]:
                        if itemKey not in allDict:
                            allDict[itemKey] = 0
                    allChampsBuilderCounts[itemKey] += builderCount
                    allChampsSellerCounts[itemKey] += sellerCount
                    allChampsBuildTimeSums[itemKey] += buildTimeSum
                    allChampsPriorityScoreSums[itemKey] += priorityScoreSum
                    if builderCount != 0:
                        itemPickRate = builderCount / mageCount
                        itemSellRate = sellerCount / builderCount
                        itemBuildTime = buildTimeSum / builderCount
                        itemPriorityScore = priorityScoreSum / builderCount
                        
                        stats[versionKey][typeKey][champKey][itemKey] = {"pickRate":itemPickRate, "sellRate":itemSellRate, "buildTime":itemBuildTime, "priorityScore":itemPriorityScore}

        for itemKey in counts[versionKey][typeKey]["Anivia"]:
            if itemKey not in {"mageCount","totalCount"}:
                stats[versionKey][typeKey]["all"][itemKey] = {"pickRate":allChampsBuilderCounts[itemKey] / allChampsMageCount,
                                                          "sellRate":allChampsSellerCounts[itemKey] / allChampsBuilderCounts[itemKey],
                                                          "buildTime":allChampsBuildTimeSums[itemKey] / allChampsBuilderCounts[itemKey],
                                                          "priorityScore":allChampsPriorityScoreSums[itemKey] / allChampsBuilderCounts[itemKey]}

print("Making HTML tables...")
# Table 1: for each champKey and for each type, a table of items and stats.
for typeKey in {"normal", "ranked"}:
    for champKey in stats["5.11"][typeKey]:
        stream = open("tables/table_" + champKey + "_" + typeKey + ".html", 'w')
        stream.write("<!DOCTYPE html>")
        stream.write("<html>")
        stream.write("<link rel=\"stylesheet\" href=\"stylesheets/core.css\" media=\"screen\">")
        stream.write("<link rel=\"stylesheet\" href=\"stylesheets/mobile.css\" media=\"handheld, only screen and (max-device-width:640px)\">")
        stream.write("<link rel=\"stylesheet\" href=\"stylesheets/github-light.css\">")
        stream.write("<table cellspacing=\"0\" cellpadding=\"0\">")
        stream.write("<thead><tr><th><span>Item</span></th><th><span>Pick Rate</span></th><th><span>Sell Rate</span></th><th><span>Mean Build Time</span></th><th><span>Mean Priority Score</span></th></tr></thead>")
        stream.write("<tbody>")
        for itemKey in ["Blasting Wand", "Needlessly Large Rod", "Rabadon's Deathcap", "Zhonya's Hourglass", "Luden's Echo", "Rylai's Crystal Scepter", "Archangel's Staff", "Rod of Ages", "Haunting Guise", "Liandry's Torment", "Void Staff", "Nashor's Tooth", "Will of the Ancients", "Morellonomicon", "Athene's Unholy Grail"]:
            itemBeforeStats = {"pickRate":0.0, "sellRate":0.0, "buildTime":0.0, "priorityScore":0.0}
            if itemKey in stats["5.11"][typeKey][champKey]:
                itemBeforeStats = stats["5.11"][typeKey][champKey][itemKey]
            itemAfterStats = {"pickRate":0.0, "sellRate":0.0, "buildTime":0.0, "priorityScore":0.0}
            if itemKey in stats["5.14"][typeKey][champKey]:
                itemAfterStats = stats["5.14"][typeKey][champKey][itemKey]
            
            stream.write("<tr>")
            stream.write("<td class=\"lalign\"><img src=\"item_pics/" + itemKey + ".png\" alt=\"" + itemKey + "\" style=\"width:32px;height:32px;display:block;margin-left:auto;margin-right:auto;\">" + itemKey + "</td>")
            # Pick Rate
            pickAfter = 100*itemAfterStats["pickRate"]
            pickDiff = pickAfter - 100*itemBeforeStats["pickRate"]
            if pickDiff > 0:
                stream.write("<td style='color:green'>" + '{0:.2f}'.format(pickAfter) + "% (+" + '{0:.2f}'.format(pickDiff) + "%)</td>")
            elif pickDiff < 0:
                stream.write("<td style='color:red'>" + '{0:.2f}'.format(pickAfter) + "% (" + '{0:.2f}'.format(pickDiff) + "%)</td>")
            else:
                stream.write("<td>" + '{0:.2f}'.format(pickAfter) + "% (�0.00%)</td>")
            # Sell Rate
            sellAfter = 100*itemAfterStats["sellRate"]
            sellDiff = sellAfter - 100*itemBeforeStats["sellRate"]
            if sellDiff < 0:
                stream.write("<td style='color:green'>" + '{0:.2f}'.format(sellAfter) + "% (" + '{0:.2f}'.format(sellDiff) + "%)</td>")
            elif sellDiff > 0:
                stream.write("<td style='color:red'>" + '{0:.2f}'.format(sellAfter) + "% (+" + '{0:.2f}'.format(sellDiff) + "%)</td>")
            else:
                stream.write("<td>" + '{0:.2f}'.format(sellAfter) + "% (�0.00%)</td>")
            
            # Build Time
            timeAfter = itemAfterStats["buildTime"]
            timeDiff = timeAfter - itemBeforeStats["buildTime"]
            if timeDiff < 0:
                stream.write("<td style='color:green'>" + gameClock(timeAfter) + " (" + gameClock(timeDiff) + ")</td>")
            elif timeDiff > 0:
                stream.write("<td style='color:red'>" + gameClock(timeAfter) + " (+" + gameClock(timeDiff) + ")</td>")
            else:
                stream.write("<td>" + gameClock(timeAfter) + " (�0.00)</td>")
            
            # Priority Score
            if itemKey in {"Blasting Wand","Needlessly Large Rod","Haunting Guise"}:
                stream.write("<td>N/A</td>")
            else:
                scoreAfter = itemAfterStats["priorityScore"]
                scoreDiff = scoreAfter - itemBeforeStats["priorityScore"]
                if scoreDiff > 0:
                    stream.write("<td style='color:green'>" + '{0:.2f}'.format(scoreAfter) + " (+" + '{0:.2f}'.format(scoreDiff) + ")</td>")
                elif scoreDiff < 0:
                    stream.write("<td style='color:red'>" + '{0:.2f}'.format(scoreAfter) + " (" + '{0:.2f}'.format(scoreDiff) + ")</td>")
                else:
                    stream.write("<td>" + '{0:.2f}'.format(scoreAfter) + " (�0.00)</td>")
            
            stream.write("</tr>")
                

        stream.write("</tbody>")
        stream.write("</table>")
        stream.close()

print("Done")
