package com.sky.service.impl;

import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import com.sky.constant.MessageConstant;
import com.sky.dto.*;
import com.sky.entity.*;
import com.sky.mapper.*;
import com.sky.result.PageResult;
import com.sky.service.AdminOrderService;
import com.sky.vo.OrderStatisticsVO;
import com.sky.vo.OrderVO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service("adminOrderService")
@Slf4j
public class AdminOrderServiceImpl implements AdminOrderService {
    @Autowired private OrderMapper orderMapper;
    @Autowired private OrderDetailMapper orderDetailMapper;

    public PageResult conditionSearch(OrdersPageQueryDTO dto) {
        PageHelper.startPage(dto.getPage(), dto.getPageSize());
        Page<Orders> page = orderMapper.pageQuery(dto);
        return new PageResult(page.getTotal(), page.getResult());
    }

    public OrderVO details(Long id) {
        Orders orders = orderMapper.getById(id);
        List<OrderDetail> details = orderDetailMapper.getByOrderId(id);
        OrderVO vo = new OrderVO();
        BeanUtils.copyProperties(orders, vo);
        vo.setOrderDetailList(details);
        return vo;
    }

    public void confirm(Long id) {
        Orders orders = Orders.builder().id(id).status(Orders.CONFIRMED).build();
        orderMapper.update(orders);
    }

    @Transactional
    public void rejection(OrdersRejectionDTO dto) {
        Orders orders = orderMapper.getById(dto.getId());
        if (orders == null || orders.getStatus() != Orders.TO_BE_CONFIRMED) {
            throw new RuntimeException("订单状态不正确");
        }
        orders.setStatus(Orders.CANCELLED);
        orders.setRejectionReason(dto.getRejectionReason());
        orders.setCancelTime(LocalDateTime.now());
        orderMapper.update(orders);
    }

    public void delivery(Long id) {
        Orders orders = Orders.builder().id(id).status(Orders.DELIVERY_IN_PROGRESS).build();
        orderMapper.update(orders);
    }

    public void complete(Long id) {
        Orders orders = Orders.builder().id(id).status(Orders.COMPLETED).deliveryTime(LocalDateTime.now()).build();
        orderMapper.update(orders);
    }

    @Transactional
    public void cancel(OrdersCancelDTO dto) {
        Orders orders = orderMapper.getById(dto.getId());
        if (orders == null) {
            throw new RuntimeException("订单不存在");
        }
        orders.setStatus(Orders.CANCELLED);
        orders.setCancelReason(dto.getCancelReason());
        orders.setCancelTime(LocalDateTime.now());
        orderMapper.update(orders);
    }

    public OrderStatisticsVO statistics() {
        Map<String, Object> map = new HashMap<>();
        map.put("status", Orders.TO_BE_CONFIRMED);
        Integer toBeConfirmed = orderMapper.countByMap(map);
        map.put("status", Orders.CONFIRMED);
        Integer confirmed = orderMapper.countByMap(map);
        map.put("status", Orders.DELIVERY_IN_PROGRESS);
        Integer deliveryInProgress = orderMapper.countByMap(map);
        OrderStatisticsVO vo = new OrderStatisticsVO();
        vo.setToBeConfirmed(toBeConfirmed);
        vo.setConfirmed(confirmed);
        vo.setDeliveryInProgress(deliveryInProgress);
        return vo;
    }
}