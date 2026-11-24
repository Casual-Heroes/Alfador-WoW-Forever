"""Check the isolated probe without opening a WoW client."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / '.builddeps'))
from lupa.lua51 import LuaRuntime as Lua51
from lupa.lua54 import LuaRuntime as Lua54


source = (HERE / 'Probe.lua').read_text(encoding='utf-8')
for runtime in (Lua51, Lua54):
    lua = runtime()
    lua.execute('''
        secret={}
        issecretvalue=function(v) return v==secret end
        InCombatLockdown=function() return false end
        GetBuildInfo=function() return '1.60.1','71037','',16001 end
        UnitLevel=function() return 1 end
        C_Map={GetBestMapForUnit=function() return 1438 end,
               GetPlayerMapPosition=function() return {x=.55,y=.44} end}
        active=false; offerID=901
        C_QuestLog={GetNumQuestLogEntries=function() return 0 end,
            IsOnQuest=function() return active end, GetSelectedQuest=function() return 901 end,
            GetTitleForQuestID=function() return 'Synthetic starter quest' end,
            GetLogIndexForQuestID=function() return 1 end,
            GetNextWaypoint=function() return 1438,.60,.50 end,
            GetQuestsOnMap=function() return {{questID=901,x=.60,y=.50},
                {questID=777,x=secret,y=.70}} end}
        GossipFrame={IsShown=function() return true end}
        QuestFrame={IsShown=function() return true end}
        C_GossipInfo={GetAvailableQuests=function() return {{questID=901,title='Synthetic starter quest'}} end}
        GetQuestID=function() return offerID end
        GetTitleText=function() return 'Synthetic starter quest' end
        GetQuestText=function() return 'Offer description' end
        GetObjectiveText=function() return 'Find an item' end
        GetRewardXP=function() return 0 end
        GetRewardMoney=function() return 3 end
        GetNumQuestRewards=function() return 1 end
        GetNumQuestChoices=function() return 0 end
        GetQuestItemInfo=function() return 'A reward',nil,2,nil,nil,999 end
        GetQuestLogQuestText=function() return 'Journal description','Find an item' end
        GetQuestLogRewardXP=function() return 25 end
    ''')
    probe = lua.execute(source)
    baseline = probe('baseline')
    assert baseline.build == '71037' and baseline.mapID == 1438 and baseline.position.x == .55 and baseline.journalRows == 0
    assert len(baseline.mapPOIs) == 1 and baseline.quest is None
    assert probe('gossip').offers[1].questID == 901
    offer = probe('offer').quest
    assert offer.questID == 901 and offer.description == 'Offer description' and offer.xpStatus == 'zero, verify in UI'
    assert offer.rewards['items'][1].count == 2 and offer.choices.reportedCount == 0
    assert offer.waypoint.mapID == 1438 and len(offer.mapPOIs) == 1
    assert probe('journal').quest is None
    lua.execute('active=true')
    journal = probe('journal').quest
    assert journal.description == 'Journal description' and journal.xp == 25
    assert journal.rewards.status == 'unavailable' and probe('offer').quest is None
    lua.execute('active=false; GetQuestText=function() offerID=902; return "Synthetic changed offer" end')
    assert probe('offer').quest.status == 'context changed'
    lua.execute('InCombatLockdown=function() return true end')
    assert probe('baseline').status == 'observation unavailable'
    print(lua.lua_implementation, 'native-quest probe smoke assertions passed')
