package com.sky.task;

import com.alibaba.fastjson.JSON;
import com.sky.entity.Orders;
import com.sky.mapper.OrderMapper;
import com.sky.websocket.WebSocketServer;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Component
public class WebSocketTask {
    @Autowired
    private WebSocketServer webSocketServer;
    @Autowired
    private OrderMapper orderMapper;

    @Scheduled(cron = "0 */3 * * * ?")
    public void sendMessageToClient() {
        Map<String, Object> statMap = new HashMap<>();
        statMap.put("status", Orders.TO_BE_CONFIRMED);
        Integer toBeConfirmed = orderMapper.countByMap(statMap);
        statMap.put("status", Orders.CONFIRMED);
        Integer confirmed = orderMapper.countByMap(statMap);
        statMap.put("status", Orders.DELIVERY_IN_PROGRESS);
        Integer deliveryInProgress = orderMapper.countByMap(statMap);

        // 只统计需要商家处理的订单，排除待支付
        int total = (toBeConfirmed == null ? 0 : toBeConfirmed) +
                    (confirmed == null ? 0 : confirmed) +
                    (deliveryInProgress == null ? 0 : deliveryInProgress);
        if (total == 0) return;

        Map<String, Object> map = new HashMap<>();
        map.put("type", 0);
        map.put("timestamp", DateTimeFormatter.ofPattern("HH:mm:ss").format(LocalDateTime.now()));
        map.put("toBeConfirmed", toBeConfirmed == null ? 0 : toBeConfirmed);
        map.put("confirmed", confirmed == null ? 0 : confirmed);
        map.put("deliveryInProgress", deliveryInProgress == null ? 0 : deliveryInProgress);
        map.put("content", String.format("待接单:%d 已接单:%d 派送中:%d",
                toBeConfirmed == null ? 0 : toBeConfirmed,
                confirmed == null ? 0 : confirmed,
                deliveryInProgress == null ? 0 : deliveryInProgress));

        webSocketServer.sendToAllClient(JSON.toJSONString(map));
    }
}
